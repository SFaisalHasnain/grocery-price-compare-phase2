from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import uuid

class StoreLocation(BaseModel):
    address: str
    city: str
    postcode: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    distance_km: Optional[float] = None

class Store(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    brand: str
    type: str = "supermarket"  # supermarket, convenience, online
    logo_url: Optional[str] = None
    description: Optional[str] = None
    locations: List[StoreLocation] = []
    delivery_available: bool = False
    click_collect_available: bool = False
    opening_hours: Optional[Dict[str, str]] = None
    average_rating: Optional[float] = None
    price_tier: str = "medium"  # budget, medium, premium
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class StoreSearch(BaseModel):
    location: Optional[str] = None
    radius_km: float = 10.0
    delivery_only: bool = False
    store_type: Optional[str] = None
