from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.chatbot import Chatbot
from app.schemas.chatbot import ChatbotCreate, ChatbotUpdate
from app.services.user import get_user

def get_chatbot(db: Session, chatbot_id: int) -> Optional[Chatbot]:
    return db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()

def get_chatbots_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Chatbot]:
    return db.query(Chatbot).filter(Chatbot.user_id == user_id).offset(skip).limit(limit).all()

def create_chatbot(db: Session, chatbot: ChatbotCreate) -> Chatbot:
    # Verify user exists
    user = get_user(db, user_id=chatbot.user_id)
    if not user:
        raise ValueError(f"User with id {chatbot.user_id} not found")
    
    db_chatbot = Chatbot(
        user_id=chatbot.user_id,
        name=chatbot.name,
        index_id=chatbot.index_id
    )
    db.add(db_chatbot)
    db.commit()
    db.refresh(db_chatbot)
    return db_chatbot

def update_chatbot(db: Session, chatbot_id: int, chatbot: ChatbotUpdate) -> Optional[Chatbot]:
    db_chatbot = get_chatbot(db, chatbot_id)
    if not db_chatbot:
        return None
    
    update_data = chatbot.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_chatbot, field, value)
    
    db.commit()
    db.refresh(db_chatbot)
    return db_chatbot

def delete_chatbot(db: Session, chatbot_id: int) -> bool:
    db_chatbot = get_chatbot(db, chatbot_id)
    if not db_chatbot:
        return False
    db.delete(db_chatbot)
    db.commit()
    return True 