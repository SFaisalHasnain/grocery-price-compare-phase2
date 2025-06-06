from typing import List, Dict
import random
from datetime import datetime
from models.store import Store, StoreLocation
from models.product import Product, ProductPrice

# UK Grocery Stores Data
UK_STORES = [
    {
        "name": "Tesco Extra",
        "brand": "Tesco",
        "price_tier": "medium",
        "logo_url": "https://logos-world.net/wp-content/uploads/2020/09/Tesco-Logo.png",
        "description": "UK's largest supermarket chain",
        "delivery_available": True,
        "click_collect_available": True
    },
    {
        "name": "ASDA Superstore", 
        "brand": "ASDA",
        "price_tier": "budget",
        "logo_url": "https://logos-world.net/wp-content/uploads/2020/09/ASDA-Logo.png",
        "description": "Save money. Live better.",
        "delivery_available": True,
        "click_collect_available": True
    },
    {
        "name": "Sainsbury's",
        "brand": "Sainsbury's", 
        "price_tier": "medium",
        "logo_url": "https://logos-world.net/wp-content/uploads/2020/09/Sainsburys-Logo.png",
        "description": "Fresh food, clothing and general merchandise",
        "delivery_available": True,
        "click_collect_available": True
    },
    {
        "name": "Lidl",
        "brand": "Lidl",
        "price_tier": "budget",
        "logo_url": "https://logos-world.net/wp-content/uploads/2020/09/Lidl-Logo.png", 
        "description": "Big on quality, Lidl on price",
        "delivery_available": False,
        "click_collect_available": False
    },
    {
        "name": "Aldi",
        "brand": "Aldi",
        "price_tier": "budget",
        "logo_url": "https://logos-world.net/wp-content/uploads/2020/09/Aldi-Logo.png",
        "description": "Good Different",
        "delivery_available": False,
        "click_collect_available": False
    },
    {
        "name": "Waitrose",
        "brand": "Waitrose",
        "price_tier": "premium", 
        "logo_url": "https://logos-world.net/wp-content/uploads/2020/09/Waitrose-Logo.png",
        "description": "Quality food, beautifully served",
        "delivery_available": True,
        "click_collect_available": True
    },
    {
        "name": "Iceland",
        "brand": "Iceland",
        "price_tier": "budget",
        "logo_url": "https://logos-world.net/wp-content/uploads/2020/09/Iceland-Logo.png",
        "description": "Power of Frozen",
        "delivery_available": True,
        "click_collect_available": False
    },
    {
        "name": "Co-op",
        "brand": "Co-op",
        "price_tier": "medium",
        "logo_url": "https://logos-world.net/wp-content/uploads/2020/09/Co-op-Logo.png",
        "description": "Co-operative Food",
        "delivery_available": True,
        "click_collect_available": True
    },
    {
        "name": "Morrisons",
        "brand": "Morrisons", 
        "price_tier": "medium",
        "logo_url": "https://logos-world.net/wp-content/uploads/2020/09/Morrisons-Logo.png",
        "description": "It Makes It",
        "delivery_available": True,
        "click_collect_available": True
    },
    {
        "name": "Amazon Fresh",
        "brand": "Amazon",
        "price_tier": "medium",
        "logo_url": "https://logos-world.net/wp-content/uploads/2020/04/Amazon-Logo.png",
        "description": "Fresh groceries delivered",
        "delivery_available": True,
        "click_collect_available": False,
        "type": "online"
    }
]

# UK Cities for mock locations
UK_CITIES = [
    {"city": "London", "locations": ["E1 6AN", "SW1A 1AA", "W1A 0AX", "EC1A 1BB"]},
    {"city": "Manchester", "locations": ["M1 1AA", "M2 2BB", "M3 3CC"]}, 
    {"city": "Birmingham", "locations": ["B1 1AA", "B2 2BB", "B3 3CC"]},
    {"city": "Leeds", "locations": ["LS1 1AA", "LS2 2BB"]},
    {"city": "Liverpool", "locations": ["L1 1AA", "L2 2BB"]},
    {"city": "Bristol", "locations": ["BS1 1AA", "BS2 2BB"]},
]

# Product categories and items
PRODUCT_CATEGORIES = {
    "Fruits & Vegetables": [
        {"name": "Bananas", "unit": "kg", "avg_price": 1.2},
        {"name": "Apples", "unit": "kg", "avg_price": 2.5},
        {"name": "Tomatoes", "unit": "kg", "avg_price": 2.8},
        {"name": "Potatoes", "unit": "kg", "avg_price": 1.8},
        {"name": "Carrots", "unit": "kg", "avg_price": 1.5},
        {"name": "Broccoli", "unit": "each", "avg_price": 1.2},
        {"name": "Lettuce", "unit": "each", "avg_price": 0.9},
        {"name": "Onions", "unit": "kg", "avg_price": 1.3}
    ],
    "Meat & Fish": [
        {"name": "Chicken Breast", "unit": "kg", "avg_price": 8.5},
        {"name": "Beef Mince", "unit": "kg", "avg_price": 7.2},
        {"name": "Salmon Fillet", "unit": "kg", "avg_price": 18.0},
        {"name": "Pork Chops", "unit": "kg", "avg_price": 6.8}
    ],
    "Dairy & Eggs": [
        {"name": "Milk", "unit": "2L", "avg_price": 1.4},
        {"name": "Large Eggs", "unit": "dozen", "avg_price": 2.8},
        {"name": "Cheddar Cheese", "unit": "400g", "avg_price": 3.2},
        {"name": "Greek Yogurt", "unit": "500g", "avg_price": 2.1}
    ],
    "Bakery": [
        {"name": "White Bread", "unit": "800g", "avg_price": 1.1},
        {"name": "Wholemeal Bread", "unit": "800g", "avg_price": 1.3},
        {"name": "Croissants", "unit": "pack of 6", "avg_price": 2.0}
    ],
    "Pantry": [
        {"name": "Olive Oil", "unit": "500ml", "avg_price": 4.5},
        {"name": "Pasta", "unit": "500g", "avg_price": 1.2},
        {"name": "Rice", "unit": "1kg", "avg_price": 2.0},
        {"name": "Cereal", "unit": "375g", "avg_price": 3.8}
    ]
}

def generate_price_variation(base_price: float, store_tier: str) -> float:
    """Generate realistic price variations based on store tier"""
    if store_tier == "budget":
        return base_price * random.uniform(0.75, 0.95)
    elif store_tier == "premium":
        return base_price * random.uniform(1.05, 1.25)
    else:  # medium
        return base_price * random.uniform(0.90, 1.10)

async def create_mock_stores() -> List[Store]:
    """Create mock store data"""
    stores = []
    
    for store_data in UK_STORES:
        locations = []
        
        # Add locations in different cities
        for city_data in UK_CITIES[:3]:  # First 3 cities for each store
            for postcode in city_data["locations"][:2]:  # 2 locations per city
                location = StoreLocation(
                    address=f"{random.randint(1, 999)} High Street",
                    city=city_data["city"],
                    postcode=postcode,
                    latitude=random.uniform(50.0, 55.0),
                    longitude=random.uniform(-5.0, 2.0)
                )
                locations.append(location)
        
        store = Store(
            name=store_data["name"],
            brand=store_data["brand"],
            type=store_data.get("type", "supermarket"),
            logo_url=store_data["logo_url"],
            description=store_data["description"],
            locations=locations,
            delivery_available=store_data["delivery_available"],
            click_collect_available=store_data["click_collect_available"],
            price_tier=store_data["price_tier"],
            average_rating=random.uniform(3.5, 4.8)
        )
        stores.append(store)
    
    return stores

async def create_mock_products(stores: List[Store]) -> List[Product]:
    """Create mock product data with prices from different stores"""
    products = []
    
    for category, items in PRODUCT_CATEGORIES.items():
        for item in items:
            # Create prices for random stores (3-7 stores per product)
            num_stores = random.randint(3, 7)
            selected_stores = random.sample(stores, num_stores)
            
            prices = []
            for store in selected_stores:
                price = generate_price_variation(item["avg_price"], store.price_tier)
                
                product_price = ProductPrice(
                    store_id=store.id,
                    store_name=store.name,
                    price=round(price, 2),
                    unit=item["unit"],
                    availability=random.choice([True, True, True, False]),  # 75% availability
                    promotion=random.choice([None, None, None, "BOGOF", "25% OFF"]) if random.random() < 0.15 else None
                )
                prices.append(product_price)
            
            # Calculate average price and find cheapest store
            avg_price = sum(p.price for p in prices) / len(prices)
            cheapest_store = min(prices, key=lambda x: x.price).store_name
            
            product = Product(
                name=item["name"],
                category=category,
                brand=random.choice(["Own Brand", "Premium", "Value", "Organic"]),
                description=f"Fresh {item['name'].lower()}",
                prices=prices,
                average_price=round(avg_price, 2),
                cheapest_store=cheapest_store
            )
            products.append(product)
    
    return products
