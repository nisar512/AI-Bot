from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.chat_history import ChatHistoryCreate, ChatHistory, ChatHistoryResponse
from app.services.chat_history import create_chat_history, get_recent_chat_history, get_chat_history

router = APIRouter()

@router.post("/", response_model=List[ChatHistory])
def create_chat_history_endpoint(
    chatbot_id: str,
    user_message: str,
    assistant_response: str,
    db: Session = Depends(get_db)
):
    user_entry, assistant_entry = create_chat_history(
        db=db,
        chatbot_id=chatbot_id,
        user_message=user_message,
        assistant_response=assistant_response
    )
    return [user_entry, assistant_entry]

@router.get("/{chatbot_id}/recent", response_model=ChatHistoryResponse)
def get_recent_chat_history_endpoint(
    chatbot_id: str,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    messages = get_recent_chat_history(db=db, chatbot_id=chatbot_id, limit=limit)
    return {"messages": messages}

@router.get("/{chatbot_id}", response_model=ChatHistoryResponse)
def get_chat_history_endpoint(
    chatbot_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    messages = get_chat_history(db=db, chatbot_id=chatbot_id, skip=skip, limit=limit)
    return {"messages": messages} 