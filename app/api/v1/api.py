from fastapi import APIRouter
from app.api.v1.endpoints import users, auth, chatbots, access_keys

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(chatbots.router, prefix="/chatbots", tags=["chatbots"])
api_router.include_router(access_keys.router, prefix="/access-keys", tags=["access-keys"]) 