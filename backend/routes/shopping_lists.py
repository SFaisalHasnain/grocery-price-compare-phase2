from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from datetime import datetime

from models.shopping_list import (
    ShoppingList, 
    ShoppingListCreate, 
    ShoppingListUpdate,
    ShoppingListItem,
    ShoppingListItemCreate,
    ShoppingListItemUpdate,
    CategorySuggestion
)
from models.user import User
from services.auth_dependencies import get_current_user
from services.database import get_database

router = APIRouter(prefix="/shopping-lists", tags=["shopping-lists"])

# Category suggestions based on common grocery items
CATEGORY_SUGGESTIONS = {
    "fruits": CategorySuggestion(category="Fruits & Vegetables", suggested_unit="kg", typical_quantity=1.0),
    "vegetables": CategorySuggestion(category="Fruits & Vegetables", suggested_unit="kg", typical_quantity=1.0),
    "meat": CategorySuggestion(category="Meat & Fish", suggested_unit="kg", typical_quantity=0.5),
    "fish": CategorySuggestion(category="Meat & Fish", suggested_unit="kg", typical_quantity=0.5),
    "milk": CategorySuggestion(category="Dairy & Eggs", suggested_unit="2L", typical_quantity=1.0),
    "cheese": CategorySuggestion(category="Dairy & Eggs", suggested_unit="200g", typical_quantity=1.0),
    "eggs": CategorySuggestion(category="Dairy & Eggs", suggested_unit="dozen", typical_quantity=1.0),
    "bread": CategorySuggestion(category="Bakery", suggested_unit="loaf", typical_quantity=1.0),
    "rice": CategorySuggestion(category="Pantry", suggested_unit="kg", typical_quantity=1.0),
    "pasta": CategorySuggestion(category="Pantry", suggested_unit="500g", typical_quantity=1.0),
}

@router.get("/", response_model=List[ShoppingList])
async def get_shopping_lists(current_user: User = Depends(get_current_user)):
    """Get all shopping lists for the current user"""
    db = await get_database()
    
    lists_data = await db.shopping_lists.find(
        {"user_id": current_user.id}
    ).sort("updated_at", -1).to_list(length=None)
    
    return [ShoppingList(**list_data) for list_data in lists_data]

@router.post("/", response_model=ShoppingList, status_code=status.HTTP_201_CREATED)
async def create_shopping_list(
    list_create: ShoppingListCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new shopping list"""
    db = await get_database()
    
    shopping_list = ShoppingList(
        user_id=current_user.id,
        name=list_create.name,
        description=list_create.description
    )
    
    await db.shopping_lists.insert_one(shopping_list.dict())
    return shopping_list

@router.get("/{list_id}", response_model=ShoppingList)
async def get_shopping_list(
    list_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific shopping list"""
    db = await get_database()
    
    list_dict = await db.shopping_lists.find_one({
        "id": list_id,
        "user_id": current_user.id
    })
    
    if not list_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found"
        )
    
    return ShoppingList(**list_dict)

@router.put("/{list_id}", response_model=ShoppingList)
async def update_shopping_list(
    list_id: str,
    list_update: ShoppingListUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a shopping list"""
    db = await get_database()
    
    # Check if list exists and belongs to user
    existing_list = await db.shopping_lists.find_one({
        "id": list_id,
        "user_id": current_user.id
    })
    
    if not existing_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found"
        )
    
    # Update only provided fields
    update_data = {k: v for k, v in list_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.shopping_lists.update_one(
        {"id": list_id},
        {"$set": update_data}
    )
    
    # Return updated list
    updated_list_dict = await db.shopping_lists.find_one({"id": list_id})
    return ShoppingList(**updated_list_dict)

@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_list(
    list_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a shopping list"""
    db = await get_database()
    
    result = await db.shopping_lists.delete_one({
        "id": list_id,
        "user_id": current_user.id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found"
        )

@router.post("/{list_id}/items", response_model=ShoppingList, status_code=status.HTTP_201_CREATED)
async def add_item_to_list(
    list_id: str,
    item_create: ShoppingListItemCreate,
    current_user: User = Depends(get_current_user)
):
    """Add an item to a shopping list"""
    db = await get_database()
    
    # Check if list exists and belongs to user
    shopping_list = await get_shopping_list(list_id, current_user)
    
    # Create new item
    new_item = ShoppingListItem(**item_create.dict())
    
    # Add item to list
    await db.shopping_lists.update_one(
        {"id": list_id},
        {
            "$push": {"items": new_item.dict()},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    # Return updated list
    updated_list_dict = await db.shopping_lists.find_one({"id": list_id})
    return ShoppingList(**updated_list_dict)

@router.put("/{list_id}/items/{item_id}", response_model=ShoppingList)
async def update_list_item(
    list_id: str,
    item_id: str,
    item_update: ShoppingListItemUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update an item in a shopping list"""
    db = await get_database()
    
    # Check if list exists and belongs to user
    shopping_list = await get_shopping_list(list_id, current_user)
    
    # Find the item to update
    item_found = False
    for item in shopping_list.items:
        if item.id == item_id:
            item_found = True
            break
    
    if not item_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in shopping list"
        )
    
    # Update item fields
    update_data = {f"items.$.{k}": v for k, v in item_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.shopping_lists.update_one(
        {"id": list_id, "items.id": item_id},
        {"$set": update_data}
    )
    
    # Return updated list
    updated_list_dict = await db.shopping_lists.find_one({"id": list_id})
    return ShoppingList(**updated_list_dict)

@router.delete("/{list_id}/items/{item_id}", response_model=ShoppingList)
async def remove_item_from_list(
    list_id: str,
    item_id: str,
    current_user: User = Depends(get_current_user)
):
    """Remove an item from a shopping list"""
    db = await get_database()
    
    # Check if list exists and belongs to user
    await get_shopping_list(list_id, current_user)
    
    # Remove item from list
    await db.shopping_lists.update_one(
        {"id": list_id},
        {
            "$pull": {"items": {"id": item_id}},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    # Return updated list
    updated_list_dict = await db.shopping_lists.find_one({"id": list_id})
    return ShoppingList(**updated_list_dict)

@router.get("/suggestions/categories", response_model=List[CategorySuggestion])
async def get_category_suggestions(q: Optional[str] = None):
    """Get category suggestions for smart shopping lists"""
    if q:
        # Filter suggestions based on query
        query_lower = q.lower()
        matching_suggestions = []
        
        for key, suggestion in CATEGORY_SUGGESTIONS.items():
            if query_lower in key or query_lower in suggestion.category.lower():
                matching_suggestions.append(suggestion)
        
        return matching_suggestions
    
    # Return all suggestions
    return list(CATEGORY_SUGGESTIONS.values())
