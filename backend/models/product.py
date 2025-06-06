from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import uuid

class ProductPrice(BaseModel):
    store_id: str
    store_name: str
    price: float
    unit: str = "each"  # each, kg, g, l, ml, pack
    availability: bool = True
    promotion: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str
    brand: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    barcode: Optional[str] = None
    prices: List[ProductPrice] = []
    average_price: Optional[float] = None
    cheapest_store: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ProductSearch(BaseModel):
    query: str
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    store_ids: Optional[List[str]] = None
    location: Optional[str] = None
    sort_by: str = "relevance"  # relevance, price_low, price_high, name

class ProductResponse(BaseModel):
    products: List[Product]
    total: int
    page: int
    per_page: int
    categories: List[str]
