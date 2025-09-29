from fastapi import FastAPI, HTTPException, Depends, APIRouter, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import httpx
import base64
from urllib.parse import quote

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
security = HTTPBasic()

# Create the main app without a prefix
app = FastAPI(title="WordPress Management Interface", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class WordPressConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    site_url: str
    username: str
    app_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WordPressConfigCreate(BaseModel):
    site_url: str
    username: str
    app_password: str

class WordPressPost(BaseModel):
    id: int
    title: str
    content: str
    status: str
    type: str
    featured_media: Optional[int] = None
    date: str
    modified: str
    link: str
    excerpt: str

class WordPressProduct(BaseModel):
    id: int
    title: str
    content: str
    status: str
    featured_media: Optional[int] = None
    date: str
    modified: str
    link: str
    excerpt: str
    product_cat: List[int] = []
    product_tag: List[int] = []

class CreateEventRequest(BaseModel):
    title: str
    content: str
    location: str
    event_date: str
    featured_image_url: Optional[str] = None

class CreateProductRequest(BaseModel):
    title: str
    content: str
    status: str = "draft"
    featured_image_url: Optional[str] = None

# WordPress API Helper
class WordPressAPI:
    def __init__(self, site_url: str, username: str, app_password: str):
        self.site_url = site_url.rstrip('/')
        self.username = username
        self.app_password = app_password
        self.base_url = f"{self.site_url}/wp-json/wp/v2"
        
    def get_auth_header(self):
        credentials = f"{self.username}:{self.app_password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded_credentials}"}
    
    async def get(self, endpoint: str, params: Dict = None):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{endpoint}",
                params=params or {},
                headers=self.get_auth_header()
            )
            if response.status_code >= 400:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"WordPress API error: {response.text}"
                )
            return response.json()
    
    async def post(self, endpoint: str, data: Dict):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/{endpoint}",
                json=data,
                headers=self.get_auth_header()
            )
            if response.status_code >= 400:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"WordPress API error: {response.text}"
                )
            return response.json()
    
    async def put(self, endpoint: str, data: Dict):
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}/{endpoint}",
                json=data,
                headers=self.get_auth_header()
            )
            if response.status_code >= 400:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"WordPress API error: {response.text}"
                )
            return response.json()
    
    async def delete(self, endpoint: str):
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/{endpoint}",
                headers=self.get_auth_header()
            )
            if response.status_code >= 400:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"WordPress API error: {response.text}"
                )
            return response.json()

# Get WordPress config from DB
async def get_wp_config():
    config = await db.wp_config.find_one()
    if not config:
        raise HTTPException(
            status_code=404,
            detail="WordPress configuration not found. Please set up your WordPress connection first."
        )
    return WordPressConfig(**config)

# Routes
@api_router.get("/")
async def root():
    return {"message": "WordPress Management API"}

# WordPress Configuration
@api_router.post("/wp-config", response_model=WordPressConfig)
async def create_wp_config(config: WordPressConfigCreate):
    # Test connection
    wp_api = WordPressAPI(config.site_url, config.username, config.app_password)
    try:
        await wp_api.get("posts", {"per_page": 1})
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to connect to WordPress: {str(e)}"
        )
    
    # Clear existing config and save new one
    await db.wp_config.delete_many({})
    config_dict = config.dict()
    wp_config = WordPressConfig(**config_dict)
    await db.wp_config.insert_one(wp_config.dict())
    return wp_config

@api_router.get("/wp-config", response_model=WordPressConfig)
async def get_wp_config_endpoint():
    return await get_wp_config()

# Posts Management
@api_router.get("/posts", response_model=List[WordPressPost])
async def get_posts(page: int = 1, per_page: int = 10):
    config = await get_wp_config()
    wp_api = WordPressAPI(config.site_url, config.username, config.app_password)
    
    posts = await wp_api.get("posts", {
        "page": page,
        "per_page": per_page,
        "_embed": True
    })
    
    return [
        WordPressPost(
            id=post["id"],
            title=post["title"]["rendered"],
            content=post["content"]["rendered"],
            status=post["status"],
            type=post["type"],
            featured_media=post.get("featured_media"),
            date=post["date"],
            modified=post["modified"],
            link=post["link"],
            excerpt=post["excerpt"]["rendered"]
        )
        for post in posts
    ]

# Products Management  
@api_router.get("/products", response_model=List[WordPressProduct])
async def get_products(page: int = 1, per_page: int = 10):
    config = await get_wp_config()
    wp_api = WordPressAPI(config.site_url, config.username, config.app_password)
    
    products = await wp_api.get("product", {
        "page": page,
        "per_page": per_page,
        "_embed": True
    })
    
    return [
        WordPressProduct(
            id=product["id"],
            title=product["title"]["rendered"],
            content=product["content"]["rendered"],
            status=product["status"],
            featured_media=product.get("featured_media"),
            date=product["date"],
            modified=product["modified"],
            link=product["link"],
            excerpt=product["excerpt"]["rendered"],
            product_cat=product.get("product_cat", []),
            product_tag=product.get("product_tag", [])
        )
        for product in products
    ]

@api_router.post("/products", response_model=Dict)
async def create_product(product: CreateProductRequest):
    config = await get_wp_config()
    wp_api = WordPressAPI(config.site_url, config.username, config.app_password)
    
    product_data = {
        "title": product.title,
        "content": product.content,
        "status": product.status,
        "type": "product"
    }
    
    if product.featured_image_url:
        # Handle image upload logic here if needed
        pass
    
    result = await wp_api.post("product", product_data)
    return result

@api_router.put("/products/{product_id}", response_model=Dict)
async def update_product(product_id: int, product: CreateProductRequest):
    config = await get_wp_config()
    wp_api = WordPressAPI(config.site_url, config.username, config.app_password)
    
    product_data = {
        "title": product.title,
        "content": product.content,
        "status": product.status
    }
    
    result = await wp_api.put(f"product/{product_id}", product_data)
    return result

@api_router.delete("/products/{product_id}", response_model=Dict)
async def delete_product(product_id: int):
    config = await get_wp_config()
    wp_api = WordPressAPI(config.site_url, config.username, config.app_password)
    
    result = await wp_api.delete(f"product/{product_id}")
    return result

# Events Management (custom post type with multiple fallbacks)
@api_router.get("/events", response_model=List[WordPressPost])
async def get_events(page: int = 1, per_page: int = 10):
    config = await get_wp_config()
    wp_api = WordPressAPI(config.site_url, config.username, config.app_password)
    
    # Try multiple endpoints for events
    events = []
    
    # 1. Try events custom post type
    try:
        events = await wp_api.get("events", {
            "page": page,
            "per_page": per_page,
            "_embed": True
        })
        print(f"Found {len(events)} events from /events endpoint")
    except Exception as e:
        print(f"Events endpoint failed: {e}")
        
        # 2. Try event custom post type (singular)
        try:
            events = await wp_api.get("event", {
                "page": page,
                "per_page": per_page,
                "_embed": True
            })
            print(f"Found {len(events)} events from /event endpoint")
        except Exception as e2:
            print(f"Event endpoint failed: {e2}")
            
            # 3. Fallback to posts with categories containing "event"
            try:
                # Get all categories first
                categories = await wp_api.get("categories", {"search": "event"})
                if categories:
                    event_category_ids = [cat["id"] for cat in categories]
                    events = await wp_api.get("posts", {
                        "page": page,
                        "per_page": per_page,
                        "_embed": True,
                        "categories": ",".join(map(str, event_category_ids))
                    })
                    print(f"Found {len(events)} posts from event categories")
                else:
                    # 4. Final fallback - search posts by title containing "event"
                    events = await wp_api.get("posts", {
                        "page": page,
                        "per_page": per_page,
                        "_embed": True,
                        "search": "event"
                    })
                    print(f"Found {len(events)} posts from event search")
            except Exception as e3:
                print(f"Category fallback failed: {e3}")
                # Return empty list if all fail
                events = []
    
    return [
        WordPressPost(
            id=event["id"],
            title=event["title"]["rendered"],
            content=event["content"]["rendered"],
            status=event["status"],
            type=event.get("type", "post"),
            featured_media=event.get("featured_media"),
            date=event["date"],
            modified=event["modified"],
            link=event["link"],
            excerpt=event["excerpt"]["rendered"]
        )
        for event in events
    ]

@api_router.post("/events", response_model=Dict)
async def create_event(event: CreateEventRequest):
    config = await get_wp_config()
    wp_api = WordPressAPI(config.site_url, config.username, config.app_password)
    
    event_data = {
        "title": event.title,
        "content": event.content,
        "status": "publish",
        "meta": {
            "event_type": "event",
            "event_location": event.location,
            "event_date": event.event_date
        }
    }
    
    # Try multiple endpoints for creating events
    try:
        # 1. Try events custom post type
        result = await wp_api.post("events", event_data)
        print("Event created via /events endpoint")
        return result
    except Exception as e:
        print(f"Events endpoint failed: {e}")
        try:
            # 2. Try event custom post type (singular)
            result = await wp_api.post("event", event_data)
            print("Event created via /event endpoint")
            return result
        except Exception as e2:
            print(f"Event endpoint failed: {e2}")
            # 3. Fallback to posts with event category
            try:
                # Get or create event category
                categories = await wp_api.get("categories", {"search": "event"})
                if categories:
                    event_category_id = categories[0]["id"]
                else:
                    # Create event category
                    new_category = await wp_api.post("categories", {"name": "Events", "slug": "events"})
                    event_category_id = new_category["id"]
                
                event_data["categories"] = [event_category_id]
                result = await wp_api.post("posts", event_data)
                print("Event created as post with event category")
                return result
            except Exception as e3:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to create event: {str(e3)}"
                )

# WordPress Site Info
@api_router.get("/site-info")
async def get_site_info():
    config = await get_wp_config()
    wp_api = WordPressAPI(config.site_url, config.username, config.app_password)
    
    site_info = await wp_api.get("", {})
    return site_info

# Test Connection
@api_router.get("/test-connection")
async def test_wp_connection():
    try:
        config = await get_wp_config()
        wp_api = WordPressAPI(config.site_url, config.username, config.app_password)
        await wp_api.get("posts", {"per_page": 1})
        return {"status": "connected", "message": "WordPress connection successful"}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Connection failed: {str(e)}"
        )

# Check Available Post Types
@api_router.get("/post-types")
async def get_post_types():
    config = await get_wp_config()
    wp_api = WordPressAPI(config.site_url, config.username, config.app_password)
    
    try:
        post_types = await wp_api.get("types", {})
        return {
            "available_types": list(post_types.keys()),
            "details": post_types
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get post types: {str(e)}"
        )

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
