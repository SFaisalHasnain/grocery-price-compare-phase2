from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import uuid

class BasketItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    product_name: str
    store_id: str
    store_name: str
    price: float
    quantity: float = 1.0
    unit: str = "each"
    total_price: float
    added_at: datetime = Field(default_factory=datetime.utcnow)

class BasketItemCreate(BaseModel):
    product_id: str
    store_id: str
    quantity: float = 1.0

class BasketItemUpdate(BaseModel):
    quantity: Optional[float] = None

class Basket(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    items: List[BasketItem] = []
    total_cost: float = 0.0
    total_items: int = 0
    estimated_savings: Optional[float] = None
    alternative_stores: Optional[Dict[str, float]] = None  # store_id -> total_cost
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class BasketSummary(BaseModel):
    total_cost: float
    total_items: int
    estimated_savings: Optional[float] = None
    cheapest_alternative_store: Optional[str] = None
    potential_savings: Optional[float] = None
