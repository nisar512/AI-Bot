from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import users, search, scrape, chatbots
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
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(search.router, prefix=f"{settings.API_V1_STR}/search", tags=["search"])
app.include_router(scrape.router, prefix=f"{settings.API_V1_STR}/scrape", tags=["scrape"])
app.include_router(chatbots.router, prefix=f"{settings.API_V1_STR}/chatbots", tags=["chatbots"])

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