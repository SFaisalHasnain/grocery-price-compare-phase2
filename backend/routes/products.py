from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List, Optional
import re

from models.product import Product, ProductSearch, ProductResponse
from models.user import User
from services.auth_dependencies import get_current_user
from services.database import get_database

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/search", response_model=ProductResponse)
async def search_products(
    q: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    store_ids: Optional[str] = Query(None, description="Comma-separated store IDs"),
    sort_by: str = Query("relevance", description="Sort by: relevance, price_low, price_high, name"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(12, ge=1, le=50, description="Items per page"),
    current_user: User = Depends(get_current_user)
):
    """Search products with authentication required"""
    return await _search_products_internal(q, category, min_price, max_price, store_ids, sort_by, page, per_page)

@router.get("/guest-search", response_model=ProductResponse)
async def guest_search_products(
    q: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    store_ids: Optional[str] = Query(None, description="Comma-separated store IDs"),
    sort_by: str = Query("relevance", description="Sort by: relevance, price_low, price_high, name"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(12, ge=1, le=50, description="Items per page")
):
    """Search products without authentication (guest access)"""
    return await _search_products_internal(q, category, min_price, max_price, store_ids, sort_by, page, per_page)

async def _search_products_internal(
    q: str,
    category: Optional[str],
    min_price: Optional[float],
    max_price: Optional[float],
    store_ids: Optional[str],
    sort_by: str,
    page: int,
    per_page: int
) -> ProductResponse:
    """Internal search function used by both authenticated and guest endpoints"""
    db = await get_database()
    
    # Build search query
    search_filter = {}
    
    # Text search
    if q:
        search_filter["$text"] = {"$search": q}
    
    # Category filter
    if category:
        search_filter["category"] = category
    
    # Price filter
    price_filter = {}
    if min_price is not None:
        price_filter["$gte"] = min_price
    if max_price is not None:
        price_filter["$lte"] = max_price
    
    if price_filter:
        search_filter["average_price"] = price_filter
    
    # Store filter
    if store_ids:
        store_id_list = [sid.strip() for sid in store_ids.split(",")]
        search_filter["prices.store_id"] = {"$in": store_id_list}
    
    # Build sort criteria
    sort_criteria = []
    if sort_by == "price_low":
        sort_criteria = [("average_price", 1)]
    elif sort_by == "price_high":
        sort_criteria = [("average_price", -1)]
    elif sort_by == "name":
        sort_criteria = [("name", 1)]
    else:  # relevance (default)
        if q:
            sort_criteria = [("score", {"$meta": "textScore"})]
        else:
            sort_criteria = [("name", 1)]
    
    # Execute search with pagination
    skip = (page - 1) * per_page
    
    cursor = db.products.find(search_filter)
    if sort_criteria:
        cursor = cursor.sort(sort_criteria)
    
    # Get total count
    total = await db.products.count_documents(search_filter)
    
    # Get paginated results
    products_data = await cursor.skip(skip).limit(per_page).to_list(length=per_page)
    products = [Product(**product) for product in products_data]
    
    # Get available categories for filtering
    pipeline = [
        {"$match": search_filter},
        {"$group": {"_id": "$category"}},
        {"$sort": {"_id": 1}}
    ]
    categories_cursor = db.products.aggregate(pipeline)
    categories = [doc["_id"] async for doc in categories_cursor]
    
    return ProductResponse(
        products=products,
        total=total,
        page=page,
        per_page=per_page,
        categories=categories
    )

@router.get("/categories", response_model=List[str])
async def get_categories():
    """Get all product categories"""
    db = await get_database()
    
    pipeline = [
        {"$group": {"_id": "$category"}},
        {"$sort": {"_id": 1}}
    ]
    
    categories_cursor = db.products.aggregate(pipeline)
    categories = [doc["_id"] async for doc in categories_cursor]
    
    return categories

@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Get a specific product by ID"""
    db = await get_database()
    
    product_dict = await db.products.find_one({"id": product_id})
    if not product_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return Product(**product_dict)

@router.get("/{product_id}/price-history")
async def get_product_price_history(product_id: str):
    """Get price history for a product (placeholder for future implementation)"""
    # This would typically involve storing historical price data
    # For now, return current prices
    product = await get_product(product_id)
    return {
        "product_id": product_id,
        "current_prices": product.prices,
        "message": "Historical data not yet implemented"
    }
