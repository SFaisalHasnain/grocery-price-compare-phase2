from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import uuid

class ShoppingListItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: Optional[str] = None
    product_name: str
    quantity: float = 1.0
    unit: str = "each"
    category: Optional[str] = None
    notes: Optional[str] = None
    completed: bool = False
    estimated_price: Optional[float] = None
    actual_price: Optional[float] = None
    store_preference: Optional[str] = None

class ShoppingListCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ShoppingListUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ShoppingList(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    description: Optional[str] = None
    items: List[ShoppingListItem] = []
    total_estimated_cost: Optional[float] = None
    total_actual_cost: Optional[float] = None
    is_shared: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ShoppingListItemCreate(BaseModel):
    product_name: str
    quantity: float = 1.0
    unit: str = "each"
    category: Optional[str] = None
    notes: Optional[str] = None

class ShoppingListItemUpdate(BaseModel):
    product_name: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    category: Optional[str] = None
    notes: Optional[str] = None
    completed: Optional[bool] = None

class CategorySuggestion(BaseModel):
    category: str
    suggested_unit: str
    typical_quantity: float
