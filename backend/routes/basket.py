from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Optional

from models.basket import Basket, BasketItem, BasketItemCreate, BasketItemUpdate, BasketSummary
from models.user import User
from models.product import Product
from routes.auth import get_current_user
from services.database import get_database
from datetime import datetime

router = APIRouter(prefix="/basket", tags=["basket"])

@router.get("/", response_model=Basket)
async def get_basket(current_user: User = Depends(get_current_user)):
    """Get current user's basket"""
    db = await get_database()
    
    basket_dict = await db.baskets.find_one({"user_id": current_user.id})
    
    if not basket_dict:
        # Create empty basket if none exists
        basket = Basket(user_id=current_user.id)
        await db.baskets.insert_one(basket.dict())
        return basket
    
    return Basket(**basket_dict)

@router.post("/items", response_model=Basket, status_code=status.HTTP_201_CREATED)
async def add_item_to_basket(
    item_create: BasketItemCreate,
    current_user: User = Depends(get_current_user)
):
    """Add an item to the basket"""
    db = await get_database()
    
    # Get product details
    product_dict = await db.products.find_one({"id": item_create.product_id})
    if not product_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    product = Product(**product_dict)
    
    # Find store price
    store_price = None
    for price in product.prices:
        if price.store_id == item_create.store_id:
            store_price = price
            break
    
    if not store_price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not available at this store"
        )
    
    # Get or create basket
    basket = await get_basket(current_user)
    
    # Check if item already exists in basket
    existing_item = None
    for item in basket.items:
        if item.product_id == item_create.product_id and item.store_id == item_create.store_id:
            existing_item = item
            break
    
    if existing_item:
        # Update quantity of existing item
        existing_item.quantity += item_create.quantity
        existing_item.total_price = existing_item.quantity * existing_item.price
    else:
        # Add new item
        new_item = BasketItem(
            product_id=item_create.product_id,
            product_name=product.name,
            store_id=item_create.store_id,
            store_name=store_price.store_name,
            price=store_price.price,
            quantity=item_create.quantity,
            unit=store_price.unit,
            total_price=store_price.price * item_create.quantity
        )
        basket.items.append(new_item)
    
    # Recalculate basket totals
    basket = await _recalculate_basket_totals(basket, db)
    
    # Save updated basket
    await db.baskets.update_one(
        {"user_id": current_user.id},
        {"$set": basket.dict()},
        upsert=True
    )
    
    return basket

@router.put("/items/{item_id}", response_model=Basket)
async def update_basket_item(
    item_id: str,
    item_update: BasketItemUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update an item in the basket"""
    db = await get_database()
    basket = await get_basket(current_user)
    
    # Find item to update
    item_found = False
    for item in basket.items:
        if item.id == item_id:
            if item_update.quantity is not None:
                item.quantity = item_update.quantity
                item.total_price = item.quantity * item.price
            item_found = True
            break
    
    if not item_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in basket"
        )
    
    # Recalculate basket totals
    basket = await _recalculate_basket_totals(basket, db)
    
    # Save updated basket
    await db.baskets.update_one(
        {"user_id": current_user.id},
        {"$set": basket.dict()}
    )
    
    return basket

@router.delete("/items/{item_id}", response_model=Basket)
async def remove_item_from_basket(
    item_id: str,
    current_user: User = Depends(get_current_user)
):
    """Remove an item from the basket"""
    db = await get_database()
    basket = await get_basket(current_user)
    
    # Remove item
    original_length = len(basket.items)
    basket.items = [item for item in basket.items if item.id != item_id]
    
    if len(basket.items) == original_length:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in basket"
        )
    
    # Recalculate basket totals
    basket = await _recalculate_basket_totals(basket, db)
    
    # Save updated basket
    await db.baskets.update_one(
        {"user_id": current_user.id},
        {"$set": basket.dict()}
    )
    
    return basket

@router.delete("/", response_model=Basket)
async def clear_basket(current_user: User = Depends(get_current_user)):
    """Clear all items from the basket"""
    db = await get_database()
    
    basket = Basket(
        user_id=current_user.id,
        items=[],
        total_cost=0.0,
        total_items=0,
        updated_at=datetime.utcnow()
    )
    
    await db.baskets.update_one(
        {"user_id": current_user.id},
        {"$set": basket.dict()},
        upsert=True
    )
    
    return basket

@router.get("/summary", response_model=BasketSummary)
async def get_basket_summary(current_user: User = Depends(get_current_user)):
    """Get basket summary with potential savings"""
    basket = await get_basket(current_user)
    
    return BasketSummary(
        total_cost=basket.total_cost,
        total_items=basket.total_items,
        estimated_savings=basket.estimated_savings,
        cheapest_alternative_store=_get_cheapest_alternative_store(basket),
        potential_savings=_calculate_potential_savings(basket)
    )

async def _recalculate_basket_totals(basket: Basket, db) -> Basket:
    """Recalculate basket totals and find alternatives"""
    total_cost = sum(item.total_price for item in basket.items)
    total_items = sum(item.quantity for item in basket.items)
    
    # Calculate alternative store costs
    alternative_stores = await _calculate_alternative_store_costs(basket, db)
    
    # Find estimated savings
    if alternative_stores:
        current_cost = total_cost
        cheapest_alternative_cost = min(alternative_stores.values())
        estimated_savings = max(0, current_cost - cheapest_alternative_cost)
    else:
        estimated_savings = None
    
    basket.total_cost = round(total_cost, 2)
    basket.total_items = int(total_items)
    basket.estimated_savings = estimated_savings
    basket.alternative_stores = alternative_stores
    basket.updated_at = datetime.utcnow()
    
    return basket

async def _calculate_alternative_store_costs(basket: Basket, db) -> Dict[str, float]:
    """Calculate total cost if shopping at alternative stores"""
    if not basket.items:
        return {}
    
    # Get all unique product IDs
    product_ids = list(set(item.product_id for item in basket.items))
    
    # Get all products with their prices
    products_data = await db.products.find(
        {"id": {"$in": product_ids}}
    ).to_list(length=None)
    
    products = {p["id"]: Product(**p) for p in products_data}
    
    # Calculate costs per store
    store_costs = {}
    
    for item in basket.items:
        product = products.get(item.product_id)
        if not product:
            continue
        
        for price in product.prices:
            if price.availability and price.store_id != item.store_id:
                store_id = price.store_id
                item_cost = price.price * item.quantity
                
                if store_id not in store_costs:
                    store_costs[store_id] = 0
                store_costs[store_id] += item_cost
    
    return {k: round(v, 2) for k, v in store_costs.items()}

def _get_cheapest_alternative_store(basket: Basket) -> Optional[str]:
    """Get the cheapest alternative store"""
    if not basket.alternative_stores:
        return None
    
    return min(basket.alternative_stores.keys(), key=lambda k: basket.alternative_stores[k])

def _calculate_potential_savings(basket: Basket) -> Optional[float]:
    """Calculate potential savings by switching to cheapest alternative"""
    if not basket.alternative_stores:
        return None
    
    cheapest_cost = min(basket.alternative_stores.values())
    return max(0, round(basket.total_cost - cheapest_cost, 2))
