from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.chatbot import Chatbot
from app.schemas.document import DocumentCreate, Document
from app.services.elasticsearch import add_document, search_documents
from datetime import datetime

def create_document(db: Session, document: DocumentCreate) -> Document:
    """
    Create a new document in Elasticsearch for a specific chatbot
    """
    # Get chatbot to verify it exists and get its index_id
    chatbot = db.query(Chatbot).filter(Chatbot.id == document.chatbot_id).first()
    if not chatbot:
        raise ValueError(f"Chatbot with id {document.chatbot_id} not found")
    
    if not chatbot.index_id:
        raise ValueError(f"Chatbot {chatbot.id} does not have an associated index")
    
    # Add document to Elasticsearch
    doc_id = add_document(
        index_id=chatbot.index_id,
        content=document.content,
        metadata=document.metadata
    )
    
    # Create and return document object
    return Document(
        id=doc_id,
        chatbot_id=document.chatbot_id,
        content=document.content,
        metadata=document.metadata,
        created_at=datetime.utcnow()
    )

def search_documents_for_chatbot(db: Session, chatbot_id: int, query: str, size: int = 10) -> list[Dict[str, Any]]:
    """
    Search documents for a specific chatbot using semantic search
    """
    # Get chatbot to verify it exists and get its index_id
    chatbot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
    if not chatbot:
        raise ValueError(f"Chatbot with id {chatbot_id} not found")
    
    if not chatbot.index_id:
        raise ValueError(f"Chatbot {chatbot.id} does not have an associated index")
    
    # Search documents in Elasticsearch
    return search_documents(
        index_id=chatbot.index_id,
        query=query,
        size=size
    ) 