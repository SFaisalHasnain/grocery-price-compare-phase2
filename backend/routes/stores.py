from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional

from models.store import Store, StoreSearch
from services.database import get_database

router = APIRouter(prefix="/stores", tags=["stores"])

@router.get("/", response_model=List[Store])
async def get_stores(
    location: Optional[str] = Query(None, description="Filter by location (city or postcode)"),
    delivery_only: bool = Query(False, description="Show only stores with delivery"),
    store_type: Optional[str] = Query(None, description="Filter by store type"),
    radius_km: float = Query(50.0, description="Search radius in kilometers")
):
    """Get all stores with optional filtering"""
    db = await get_database()
    
    # Build filter query
    filter_query = {}
    
    if delivery_only:
        filter_query["delivery_available"] = True
    
    if store_type:
        filter_query["type"] = store_type
    
    if location:
        # Simple location matching (in production, would use geospatial queries)
        location_lower = location.lower()
        filter_query["$or"] = [
            {"locations.city": {"$regex": location_lower, "$options": "i"}},
            {"locations.postcode": {"$regex": location_lower, "$options": "i"}},
            {"locations.address": {"$regex": location_lower, "$options": "i"}}
        ]
    
    stores_data = await db.stores.find(filter_query).sort("name", 1).to_list(length=None)
    
    stores = []
    for store_data in stores_data:
        store = Store(**store_data)
        
        # If location is specified, calculate distances (mock implementation)
        if location:
            for store_location in store.locations:
                # Mock distance calculation - in production would use proper geolocation
                store_location.distance_km = round(abs(hash(location + store_location.city)) % 50, 1)
        
        stores.append(store)
    
    return stores

@router.get("/{store_id}", response_model=Store)
async def get_store(store_id: str):
    """Get a specific store by ID"""
    db = await get_database()
    
    store_dict = await db.stores.find_one({"id": store_id})
    if not store_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    
    return Store(**store_dict)

@router.get("/{store_id}/products")
async def get_store_products(
    store_id: str,
    category: Optional[str] = Query(None, description="Filter by category"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page")
):
    """Get products available at a specific store"""
    db = await get_database()
    
    # Verify store exists
    store_dict = await db.stores.find_one({"id": store_id})
    if not store_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    
    # Build filter for products available at this store
    filter_query = {
        "prices": {
            "$elemMatch": {
                "store_id": store_id,
                "availability": True
            }
        }
    }
    
    if category:
        filter_query["category"] = category
    
    # Execute query with pagination
    skip = (page - 1) * per_page
    
    products_data = await db.products.find(filter_query) \
        .sort("name", 1) \
        .skip(skip) \
        .limit(per_page) \
        .to_list(length=per_page)
    
    total = await db.products.count_documents(filter_query)
    
    # Filter prices to only show this store's prices
    for product_data in products_data:
        product_data["prices"] = [
            price for price in product_data["prices"] 
            if price["store_id"] == store_id
        ]
    
    return {
        "store_id": store_id,
        "products": products_data,
        "total": total,
        "page": page,
        "per_page": per_page
    }

@router.get("/nearby/search")
async def search_nearby_stores(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius_km: float = Query(10.0, description="Search radius in kilometers"),
    delivery_only: bool = Query(False, description="Show only stores with delivery")
):
    """Search for stores near a specific location (mock implementation)"""
    db = await get_database()
    
    # Build filter query
    filter_query = {}
    if delivery_only:
        filter_query["delivery_available"] = True
    
    stores_data = await db.stores.find(filter_query).to_list(length=None)
    
    nearby_stores = []
    for store_data in stores_data:
        store = Store(**store_data)
        
        # Mock distance calculation for each location
        for location in store.locations:
            # Simple distance calculation (in production would use proper geospatial formulas)
            mock_distance = abs(hash(f"{lat}{lng}{location.latitude}{location.longitude}")) % 20
            location.distance_km = round(mock_distance, 1)
            
            # Only include stores within radius
            if location.distance_km <= radius_km:
                nearby_stores.append(store)
                break  # Only need one location within radius
    
    # Sort by distance
    nearby_stores.sort(key=lambda s: min(loc.distance_km or 999 for loc in s.locations))
    
    return nearby_stores
