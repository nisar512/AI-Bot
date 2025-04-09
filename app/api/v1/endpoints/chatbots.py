from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.chatbot import Chatbot, ChatbotCreate, ChatbotUpdate
from app.services.chatbot import (
    get_chatbot,
    get_chatbots_by_user,
    create_chatbot,
    update_chatbot,
    delete_chatbot
)

router = APIRouter()

@router.post("/", response_model=Chatbot, status_code=status.HTTP_201_CREATED)
def create_new_chatbot(chatbot: ChatbotCreate, db: Session = Depends(get_db)):
    """Create a new chatbot."""
    try:
        return create_chatbot(db=db, chatbot=chatbot)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating chatbot: {str(e)}"
        )

@router.get("/user/{user_id}", response_model=List[Chatbot])
def read_user_chatbots(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all chatbots for a specific user."""
    chatbots = get_chatbots_by_user(db, user_id=user_id, skip=skip, limit=limit)
    return chatbots

@router.get("/{chatbot_id}", response_model=Chatbot)
def read_chatbot(chatbot_id: int, db: Session = Depends(get_db)):
    """Get a specific chatbot by ID."""
    db_chatbot = get_chatbot(db, chatbot_id=chatbot_id)
    if db_chatbot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot not found"
        )
    return db_chatbot

@router.put("/{chatbot_id}", response_model=Chatbot)
def update_existing_chatbot(
    chatbot_id: int,
    chatbot: ChatbotUpdate,
    db: Session = Depends(get_db)
):
    """Update a chatbot."""
    db_chatbot = update_chatbot(db=db, chatbot_id=chatbot_id, chatbot=chatbot)
    if db_chatbot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot not found"
        )
    return db_chatbot

@router.delete("/{chatbot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_chatbot(chatbot_id: int, db: Session = Depends(get_db)):
    """Delete a chatbot."""
    if not delete_chatbot(db=db, chatbot_id=chatbot_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot not found"
        )
    return None 