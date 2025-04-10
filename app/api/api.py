from fastapi import APIRouter
from app.api.endpoints import users, auth, chatbots, documents

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(chatbots.router, prefix="/chatbots", tags=["chatbots"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"]) 