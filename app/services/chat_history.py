from sqlalchemy.orm import Session
from app.models.chat_history import ChatHistory
from app.schemas.chat_history import ChatHistoryCreate
from typing import List, Tuple

def create_chat_history_entry(db: Session, session_id: str, chatbot_id: int, message: str, role: str) -> ChatHistory:
    db_chat_history = ChatHistory(
        session_id=session_id,
        chatbot_id=chatbot_id,
        message=message,
        role=role
    )
    db.add(db_chat_history)
    db.commit()
    db.refresh(db_chat_history)
    return db_chat_history

def create_chat_history(db: Session, session_id: str, chatbot_id: int, user_message: str, assistant_response: str) -> Tuple[ChatHistory, ChatHistory]:
    # Store user message
    user_entry = create_chat_history_entry(db, session_id, chatbot_id, user_message, "user")
    # Store assistant response
    assistant_entry = create_chat_history_entry(db, session_id, chatbot_id, assistant_response, "assistant")
    return user_entry, assistant_entry

def get_recent_chat_history(db: Session, session_id: str, limit: int = 5) -> List[ChatHistory]:
    return db.query(ChatHistory)\
        .filter(ChatHistory.session_id == session_id)\
        .order_by(ChatHistory.created_at.desc())\
        .limit(limit * 2)\
        .all()

def get_chat_history(db: Session, session_id: str, skip: int = 0, limit: int = 100) -> List[ChatHistory]:
    return db.query(ChatHistory)\
        .filter(ChatHistory.session_id == session_id)\
        .order_by(ChatHistory.created_at.desc())\
        .offset(skip * 2)\
        .limit(limit * 2)\
        .all() 