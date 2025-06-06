from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from pathlib import Path
from dotenv import load_dotenv

# Import services
import sys
import os
sys.path.append(os.path.dirname(__file__))

from services.database import connect_to_mongo, close_mongo_connection, get_database
from services.mock_data import create_mock_stores, create_mock_products

# Import routes
from routes.auth import router as auth_router
from routes.products import router as products_router
from routes.shopping_lists import router as shopping_lists_router
from routes.basket import router as basket_router
from routes.stores import router as stores_router

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Grocery Price Comparison API")
    await connect_to_mongo()
    await initialize_mock_data()
    yield
    # Shutdown
    logger.info("Shutting down Grocery Price Comparison API")
    await close_mongo_connection()

# Create the main app
app = FastAPI(
    title="Grocery Price Comparison API",
    description="API for comparing grocery prices across UK stores",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes with /api prefix
app.include_router(auth_router, prefix="/api")
app.include_router(products_router, prefix="/api")
app.include_router(shopping_lists_router, prefix="/api")
app.include_router(basket_router, prefix="/api")
app.include_router(stores_router, prefix="/api")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Grocery Price Comparison API v2.0",
        "docs": "/docs",
        "status": "running"
    }

# API root endpoint
@app.get("/api")
async def api_root():
    return {
        "message": "Grocery Price Comparison API v2.0",
        "version": "2.0.0",
        "endpoints": {
            "authentication": "/api/auth/",
            "products": "/api/products/",
            "shopping_lists": "/api/shopping-lists/",
            "basket": "/api/basket/",
            "stores": "/api/stores/"
        }
    }

# Health check endpoint
@app.get("/api/health")
async def health_check():
    try:
        db = await get_database()
        # Simple database connectivity check
        await db.command("ping")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

async def initialize_mock_data():
    """Initialize the database with mock data if it's empty"""
    try:
        db = await get_database()
        
        # Check if data already exists
        store_count = await db.stores.count_documents({})
        product_count = await db.products.count_documents({})
        
        if store_count == 0:
            logger.info("Initializing mock store data...")
            stores = await create_mock_stores()
            await db.stores.insert_many([store.dict() for store in stores])
            logger.info(f"Inserted {len(stores)} stores")
            
            if product_count == 0:
                logger.info("Initializing mock product data...")
                products = await create_mock_products(stores)
                await db.products.insert_many([product.dict() for product in products])
                logger.info(f"Inserted {len(products)} products")
        else:
            logger.info("Database already contains data, skipping initialization")
            
    except Exception as e:
        logger.error(f"Failed to initialize mock data: {e}")
        # Don't fail startup if mock data initialization fails
        
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
