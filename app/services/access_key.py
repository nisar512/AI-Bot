from sqlalchemy.orm import Session
from app.models.access_key import AccessKey
from app.models.chatbot import Chatbot
from app.schemas.access_key import AccessKeyCreate
from datetime import datetime, timedelta, timezone
import secrets
from fastapi import HTTPException, status

def generate_access_key() -> str:
    """Generate a random access key"""
    return secrets.token_urlsafe(32)

def create_access_key(db: Session, access_key: AccessKeyCreate) -> AccessKey:
    """Create a new access key for a chatbot"""
    # Verify chatbot exists
    chatbot = db.query(Chatbot).filter(Chatbot.id == access_key.chatbot_id).first()
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot not found"
        )

    # Generate unique key
    key = generate_access_key()
    while db.query(AccessKey).filter(AccessKey.key == key).first():
        key = generate_access_key()

    # Set expiration date to 1 month from now if not provided
    now = datetime.now(timezone.utc)
    expires_at = access_key.expires_at or (now + timedelta(days=30))
    
    # Ensure expires_at is timezone-aware
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    # Create access key
    db_access_key = AccessKey(
        key=key,
        chatbot_id=access_key.chatbot_id,
        expires_at=expires_at
    )
    db.add(db_access_key)
    db.commit()
    db.refresh(db_access_key)
    return db_access_key

def get_access_key(db: Session, key: str) -> AccessKey:
    """Get access key by key"""
    access_key = db.query(AccessKey).filter(AccessKey.key == key).first()
    if not access_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Access key not found"
        )
    return access_key

def validate_access_key(db: Session, key: str) -> AccessKey:
    """Validate access key and return it if valid"""
    access_key = get_access_key(db, key)
    
    # Check if key is active
    if not access_key.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access key is inactive"
        )
    
    # Check if key has expired
    now = datetime.now(timezone.utc)
    if access_key.expires_at and access_key.expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access key has expired"
        )
    
    return access_key

def deactivate_access_key(db: Session, key: str) -> AccessKey:
    """Deactivate an access key"""
    access_key = get_access_key(db, key)
    access_key.is_active = False
    db.commit()
    db.refresh(access_key)
    return access_key 