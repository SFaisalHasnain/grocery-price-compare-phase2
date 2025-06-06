from motor.motor_asyncio import AsyncIOMotorClient
import os
from typing import Optional

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

db = Database()

async def get_database():
    return db.database

async def connect_to_mongo():
    """Create database connection"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'grocery_app')
    
    db.client = AsyncIOMotorClient(mongo_url)
    db.database = db.client[db_name]
    
    # Create indexes for better performance
    await create_indexes()
    
async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()

async def create_indexes():
    """Create database indexes for optimal queries"""
    if db.database is None:
        return
        
    # User indexes
    await db.database.users.create_index("email", unique=True)
    
    # Product indexes
    await db.database.products.create_index([("name", "text"), ("description", "text")])
    await db.database.products.create_index("category")
    await db.database.products.create_index("prices.store_id")
    await db.database.products.create_index("average_price")
    
    # Shopping list indexes
    await db.database.shopping_lists.create_index("user_id")
    await db.database.shopping_lists.create_index("created_at")
    
    # Basket indexes
    await db.database.baskets.create_index("user_id")
    
    # Store indexes
    await db.database.stores.create_index("name")
    await db.database.stores.create_index("brand")
