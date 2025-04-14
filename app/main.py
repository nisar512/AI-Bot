from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import auth, chatbots, access_keys, scrape
from app.core.config import settings
from app.core.elastic import elasticsearch_client
from app.core.selenium import selenium_client

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(chatbots.router, prefix="/api/v1/chatbots", tags=["chatbots"])
app.include_router(access_keys.router, prefix="/api/v1/access-keys", tags=["access-keys"])
app.include_router(scrape.router, prefix="/api/v1/scrape", tags=["scrape"])

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    await elasticsearch_client.init()
    selenium_client.init()

@app.on_event("shutdown")
async def shutdown_event():
    """Close services on shutdown."""
    await elasticsearch_client.close()
    selenium_client.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI Backend"} 