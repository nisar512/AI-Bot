from sqlalchemy.orm import Session
from app.models.session import Session
import uuid
from typing import Optional, List
from sqlalchemy import desc
from app.models.chatbot import Chatbot
from app.models.chat_history import ChatHistory

def create_session(db: Session, chatbot_id: int) -> Session:
    session_id = str(uuid.uuid4())
    db_session = Session(
        id=session_id,
        chatbot_id=chatbot_id
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_session(db: Session, session_id: str) -> Optional[Session]:
    return db.query(Session).filter(Session.id == session_id).first()

def get_or_create_session(db: Session, session_id: Optional[str], chatbot_id: int) -> Session:
    if session_id:
        session = get_session(db, session_id)
        if session:
            return session
    return create_session(db, chatbot_id)

def get_user_sessions_with_first_message(db: Session, user_id: int) -> List[dict]:
    # Get all sessions for the user's chatbots
    sessions = db.query(Session)\
        .join(Chatbot, Session.chatbot_id == Chatbot.id)\
        .filter(Chatbot.user_id == user_id)\
        .all()
    
    result = []
    for session in sessions:
        # Get the first message for each session
        first_message = db.query(ChatHistory)\
            .filter(ChatHistory.session_id == session.id)\
            .order_by(ChatHistory.created_at)\
            .first()
        
        result.append({
            "id": session.id,
            "chatbot_id": session.chatbot_id,
            "chatbot_name": session.chatbot.name,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "first_message": first_message.message if first_message else None
        })
    
    return result 