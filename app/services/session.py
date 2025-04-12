from sqlalchemy.orm import Session
from app.models.session import Session
import uuid
from typing import Optional

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