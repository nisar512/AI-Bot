from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.chatbot import Chatbot
from app.schemas.chatbot import ChatbotCreate, ChatbotUpdate
from app.services.user import get_user
from app.services.elasticsearch import create_bot_index

def get_chatbot(db: Session, chatbot_id: int) -> Optional[Chatbot]:
    return db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()

def get_chatbots_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Chatbot]:
    return db.query(Chatbot).filter(Chatbot.user_id == user_id).offset(skip).limit(limit).all()

def create_chatbot(db: Session, chatbot: ChatbotCreate) -> Chatbot:
    # Verify user exists
    user = get_user(db, user_id=chatbot.user_id)
    if not user:
        raise ValueError(f"User with id {chatbot.user_id} not found")
    
    # Create chatbot in database first to get the ID
    db_chatbot = Chatbot(
        user_id=chatbot.user_id,
        name=chatbot.name
    )
    db.add(db_chatbot)
    db.commit()
    db.refresh(db_chatbot)
    
    # Generate index_id and create Elasticsearch index
    index_id = f"bot_{db_chatbot.id}"
    if create_bot_index(index_id):
        # Update chatbot with the generated index_id
        db_chatbot.index_id = index_id
        db.commit()
        db.refresh(db_chatbot)
    else:
        # If index creation fails, delete the chatbot
        db.delete(db_chatbot)
        db.commit()
        raise ValueError("Failed to create Elasticsearch index")
    
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
    
    # Delete Elasticsearch index if it exists
    if db_chatbot.index_id:
        from app.services.elasticsearch import delete_bot_index
        delete_bot_index(db_chatbot.index_id)
    
    db.delete(db_chatbot)
    db.commit()
    return True 