from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class Chatbot(Base):
    __tablename__ = "chatbots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    index_id = Column(String, nullable=True)  # Can be null

    # Relationship with User
    user = relationship("User", back_populates="chatbots")
    
    # Relationship with Session
    sessions = relationship("Session", back_populates="chatbot") 