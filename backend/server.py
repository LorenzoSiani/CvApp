from fastapi import FastAPI, HTTPException, Depends, APIRouter, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, field_validator, HttpUrl
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import httpx
import base64
from urllib.parse import quote
import re
import bleach
from fastapi.security import HTTPBearer
import secrets

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

# Input validation helpers
def sanitize_html(text: str) -> str:
    """Sanitize HTML content to prevent XSS attacks"""
    if not text:
        return ""
    return bleach.clean(text, tags=['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li'], 
                       attributes={'a': ['href', 'title']}, strip=True, protocols=['http', 'https', 'mailto'])

def validate_wordpress_url(url: str) -> str:
    """Validate WordPress site URL"""
    if not url.startswith(('http://', 'https://')):
        raise ValueError('URL must start with http:// or https://')
    
    # Remove trailing slashes
    url = url.rstrip('/')
    
    # Basic URL validation
    if not re.match(r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', url):
        raise ValueError('Invalid WordPress site URL format')
    
    return url

# Models with validation
class WordPressConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    site_url: str = Field(..., max_length=500)
    username: str = Field(..., min_length=3, max_length=60)
    app_password: str = Field(..., min_length=10)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @field_validator('site_url')
    @classmethod
    def validate_site_url(cls, v):
        return validate_wordpress_url(v)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        # Remove any HTML/script content
        clean_username = bleach.clean(v, tags=[], strip=True)
        if len(clean_username) < 3:
            raise ValueError('Username must be at least 3 characters')
        return clean_username
    
    @field_validator('app_password')
    @classmethod
    def validate_app_password(cls, v):
        # WordPress app passwords are typically 24 characters
        if len(v) < 10:
            raise ValueError('Application password is too short')
        return v

class WordPressConfigCreate(BaseModel):
    site_url: str = Field(..., max_length=500)
    username: str = Field(..., min_length=3, max_length=60)
    app_password: str = Field(..., min_length=10)
    
    @field_validator('site_url')
    @classmethod
    def validate_site_url(cls, v):
        return validate_wordpress_url(v)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        clean_username = bleach.clean(v, tags=[], strip=True)
        if len(clean_username) < 3:
            raise ValueError('Username must be at least 3 characters')
        return clean_username

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
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., max_length=10000)
    
    # Meta fields
    data_evento: str = Field(..., description="Event date (YYYY-MM-DD)")
    ora_evento: str = Field(..., description="Event time (HH:MM)")
    luogo_evento: str = Field(..., min_length=1, max_length=200, description="Event venue")
    location: Optional[str] = Field(None, max_length=200, description="Additional location info")
    dj: Optional[str] = Field(None, max_length=200, description="DJ name")
    host: Optional[str] = Field(None, max_length=200, description="Host name")
    guest: Optional[str] = Field(None, max_length=500, description="Guest information")
    
    # Categories and media
    categorie_eventi: Optional[List[int]] = Field(default=[], description="Event category IDs")
    featured_media: Optional[int] = Field(None, description="Featured image media ID")
    
    @field_validator('title', 'luogo_evento', 'location', 'dj', 'host')
    @classmethod
    def sanitize_text_fields(cls, v):
        if v:
            return bleach.clean(v, tags=[], strip=True)
        return v
    
    @field_validator('content', 'guest')
    @classmethod
    def sanitize_content_fields(cls, v):
        if v:
            return sanitize_html(v)
        return v
    
    @field_validator('data_evento')
    @classmethod
    def validate_event_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Event date must be in YYYY-MM-DD format')
    
    @field_validator('ora_evento')
    @classmethod
    def validate_event_time(cls, v):
        try:
            datetime.strptime(v, '%H:%M')
            return v
        except ValueError:
            raise ValueError('Event time must be in HH:MM format')

class EventResponse(BaseModel):
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
    
    # Meta fields
    data_evento: Optional[str] = None
    ora_evento: Optional[str] = None
    luogo_evento: Optional[str] = None
    location: Optional[str] = None
    dj: Optional[str] = None
    host: Optional[str] = None
    guest: Optional[str] = None
    
    # Categories
    categorie_eventi: Optional[List[int]] = []

class CreateProductRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., max_length=10000)
    status: str = Field("draft", pattern=r'^(draft|publish|private|pending)$')
    featured_image_url: Optional[str] = Field(None, max_length=500)
    
    @field_validator('title')
    @classmethod
    def sanitize_title(cls, v):
        return bleach.clean(v, tags=[], strip=True)
    
    @field_validator('content')
    @classmethod
    def sanitize_content(cls, v):
        return sanitize_html(v)
    
    @field_validator('featured_image_url')
    @classmethod
    def validate_image_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('Image URL must start with http:// or https://')
        return v

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

# Events Management (using custom post type 'eventi')
@api_router.get("/events", response_model=List[EventResponse])
async def get_events(page: int = 1, per_page: int = 10):
    config = await get_wp_config()
    wp_api = WordPressAPI(config.site_url, config.username, config.app_password)
    
    try:
        # Use the correct endpoint for the custom post type 'eventi'
        events = await wp_api.get("eventi", {
            "page": page,
            "per_page": per_page,
            "_embed": True
        })
        print(f"Found {len(events)} events from /eventi endpoint")
        
        return [
            EventResponse(
                id=event["id"],
                title=event["title"]["rendered"],
                content=event["content"]["rendered"],
                status=event["status"],
                type=event.get("type", "evento"),
                featured_media=event.get("featured_media", 0) or None,
                date=event["date"],
                modified=event["modified"],
                link=event["link"],
                excerpt=event["excerpt"]["rendered"],
                
                # Extract meta fields
                data_evento=event.get("meta", {}).get("data_evento", [""])[0] if event.get("meta", {}).get("data_evento") else None,
                ora_evento=event.get("meta", {}).get("ora_evento", [""])[0] if event.get("meta", {}).get("ora_evento") else None,
                luogo_evento=event.get("meta", {}).get("luogo_evento", [""])[0] if event.get("meta", {}).get("luogo_evento") else None,
                location=event.get("meta", {}).get("location", [""])[0] if event.get("meta", {}).get("location") else None,
                dj=event.get("meta", {}).get("dj", [""])[0] if event.get("meta", {}).get("dj") else None,
                host=event.get("meta", {}).get("host", [""])[0] if event.get("meta", {}).get("host") else None,
                guest=event.get("meta", {}).get("guest", [""])[0] if event.get("meta", {}).get("guest") else None,
                
                # Extract categories
                categorie_eventi=event.get("categorie_eventi", [])
            )
            for event in events
        ]
        
    except Exception as e:
        print(f"Failed to fetch events from /eventi endpoint: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to fetch events: {str(e)}"
        )

@api_router.get("/events/{event_id}", response_model=WordPressPost)
async def get_event(event_id: int):
    """Get a single event by ID"""
    config = await get_wp_config()
    wp_api = WordPressAPI(config.site_url, config.username, config.app_password)
    
    try:
        event = await wp_api.get(f"eventi/{event_id}", {"_embed": True})
        
        return WordPressPost(
            id=event["id"],
            title=event["title"]["rendered"],
            content=event["content"]["rendered"],
            status=event["status"],
            type=event.get("type", "evento"),
            featured_media=event.get("featured_media"),
            date=event["date"],
            modified=event["modified"],
            link=event["link"],
            excerpt=event["excerpt"]["rendered"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Event not found: {str(e)}"
        )

@api_router.post("/events", response_model=Dict)
async def create_event(event: CreateEventRequest):
    """Create a new event using the custom post type 'eventi'"""
    config = await get_wp_config()
    wp_api = WordPressAPI(config.site_url, config.username, config.app_password)
    
    event_data = {
        "title": event.title,
        "content": event.content,
        "status": "publish",
        "meta": {
            "event_location": event.location,
            "event_date": event.event_date
        }
    }
    
    # Add featured image if provided
    if event.featured_image_url:
        event_data["featured_image_url"] = event.featured_image_url
    
    try:
        result = await wp_api.post("eventi", event_data)
        print(f"Event created via /eventi endpoint: {result.get('id')}")
        return result
        
    except Exception as e:
        print(f"Failed to create event via /eventi endpoint: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create event: {str(e)}"
        )

@api_router.put("/events/{event_id}", response_model=Dict)
async def update_event(event_id: int, event: CreateEventRequest):
    """Update an existing event"""
    config = await get_wp_config()
    wp_api = WordPressAPI(config.site_url, config.username, config.app_password)
    
    event_data = {
        "title": event.title,
        "content": event.content,
        "status": "publish",
        "meta": {
            "event_location": event.location,
            "event_date": event.event_date
        }
    }
    
    # Add featured image if provided
    if event.featured_image_url:
        event_data["featured_image_url"] = event.featured_image_url
    
    try:
        result = await wp_api.put(f"eventi/{event_id}", event_data)
        print(f"Event updated via /eventi endpoint: {event_id}")
        return result
        
    except Exception as e:
        print(f"Failed to update event {event_id}: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update event: {str(e)}"
        )

@api_router.delete("/events/{event_id}", response_model=Dict)
async def delete_event(event_id: int):
    """Delete an event"""
    config = await get_wp_config()
    wp_api = WordPressAPI(config.site_url, config.username, config.app_password)
    
    try:
        result = await wp_api.delete(f"eventi/{event_id}")
        print(f"Event deleted via /eventi endpoint: {event_id}")
        return {"success": True, "message": f"Event {event_id} deleted successfully", "data": result}
        
    except Exception as e:
        print(f"Failed to delete event {event_id}: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to delete event: {str(e)}"
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

# Test Events Endpoint Connectivity
@api_router.get("/test-events")
async def test_events_endpoint():
    """Test connectivity to the eventi endpoint"""
    config = await get_wp_config()
    wp_api = WordPressAPI(config.site_url, config.username, config.app_password)
    
    try:
        # Test read access to eventi endpoint
        response = await wp_api.get("eventi", {"per_page": 1})
        
        return {
            "success": True,
            "message": f"Successfully connected to eventi endpoint",
            "endpoint": f"{config.site_url}/wp-json/wp/v2/eventi",
            "events_found": len(response),
            "sample_event": response[0] if response else None
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to connect to eventi endpoint: {str(e)}",
            "endpoint": f"{config.site_url}/wp-json/wp/v2/eventi",
            "error": str(e)
        }

# Google Analytics Integration
from analytics_service import GoogleAnalyticsService

# Analytics Configuration Model
class AnalyticsConfig(BaseModel):
    ga4_property_id: str = Field(..., min_length=1, max_length=50)
    credentials_uploaded: bool = False

class AnalyticsConfigCreate(BaseModel):
    ga4_property_id: str = Field(..., min_length=1, max_length=50)

# Get or create analytics service
async def get_analytics_service():
    try:
        # Try to get analytics config from database
        analytics_config = await db.analytics_config.find_one()
        
        if analytics_config:
            ga_service = GoogleAnalyticsService(
                property_id=analytics_config["ga4_property_id"],
                credentials_path="/app/backend/service_account.json"
            )
            return ga_service
        else:
            # Return demo service if no config
            return GoogleAnalyticsService(property_id="demo", credentials_path=None)
    except Exception as e:
        print(f"Analytics service error: {e}")
        return GoogleAnalyticsService(property_id="demo", credentials_path=None)

# Analytics Configuration Routes
@api_router.post("/analytics-config", response_model=AnalyticsConfig)
async def create_analytics_config(config: AnalyticsConfigCreate):
    """Configure Google Analytics integration"""
    try:
        # Clear existing config
        await db.analytics_config.delete_many({})
        
        # Create new config
        config_dict = config.dict()
        analytics_config = AnalyticsConfig(**config_dict, credentials_uploaded=False)
        await db.analytics_config.insert_one(analytics_config.dict())
        
        return analytics_config
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to configure analytics: {str(e)}"
        )

@api_router.get("/analytics-config", response_model=AnalyticsConfig)
async def get_analytics_config():
    """Get current analytics configuration"""
    config = await db.analytics_config.find_one()
    if not config:
        # Return default demo config
        return AnalyticsConfig(
            ga4_property_id="demo",
            credentials_uploaded=False
        )
    return AnalyticsConfig(**config)

# Analytics Data Routes
@api_router.get("/analytics/overview")
async def get_analytics_overview(
    start_date: str = "30daysAgo",
    end_date: str = "today"
):
    """Get analytics overview metrics"""
    try:
        analytics_service = await get_analytics_service()
        metrics = await analytics_service.get_overview_metrics(start_date, end_date)
        
        return {
            "success": True,
            "data": metrics,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch analytics overview: {str(e)}"
        )

@api_router.get("/analytics/top-pages")
async def get_analytics_top_pages(
    start_date: str = "30daysAgo",
    end_date: str = "today",
    limit: int = 10
):
    """Get top pages by page views"""
    try:
        analytics_service = await get_analytics_service()
        pages = await analytics_service.get_top_pages(start_date, end_date, limit)
        
        return {
            "success": True,
            "data": pages,
            "total": len(pages)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch top pages: {str(e)}"
        )

@api_router.get("/analytics/traffic-sources")
async def get_analytics_traffic_sources(
    start_date: str = "30daysAgo",
    end_date: str = "today"
):
    """Get traffic sources breakdown"""
    try:
        analytics_service = await get_analytics_service()
        sources = await analytics_service.get_traffic_sources(start_date, end_date)
        
        return {
            "success": True,
            "data": sources
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch traffic sources: {str(e)}"
        )

@api_router.get("/analytics/daily-visitors")
async def get_analytics_daily_visitors(
    start_date: str = "30daysAgo",
    end_date: str = "today"
):
    """Get daily visitor data"""
    try:
        analytics_service = await get_analytics_service()
        daily_data = await analytics_service.get_daily_visitors(start_date, end_date)
        
        return {
            "success": True,
            "data": daily_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch daily visitors: {str(e)}"
        )

@api_router.get("/analytics/health")
async def analytics_health_check():
    """Check Google Analytics connection status"""
    try:
        analytics_service = await get_analytics_service()
        
        if analytics_service.available:
            return {
                "success": True,
                "message": "Google Analytics 4 connected",
                "property_id": analytics_service.property_id,
                "status": "connected"
            }
        else:
            return {
                "success": False,
                "message": "Google Analytics 4 not configured - using demo data",
                "property_id": "demo",
                "status": "demo_mode"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Analytics service error: {str(e)}",
            "status": "error"
        }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["*"]
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
