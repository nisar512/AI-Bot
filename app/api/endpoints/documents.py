from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.api import deps
from app.schemas.document import DocumentCreate, Document
from app.services import document as document_service

router = APIRouter()

@router.post("/", response_model=Document)
def create_document(
    document: DocumentCreate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """
    Create a new document for a chatbot
    """
    try:
        return document_service.create_document(db=db, document=document)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/{chatbot_id}", response_model=List[Dict[str, Any]])
def search_documents(
    chatbot_id: int,
    query: str,
    size: int = 10,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """
    Search documents for a specific chatbot using semantic search
    """
    try:
        return document_service.search_documents_for_chatbot(
            db=db,
            chatbot_id=chatbot_id,
            query=query,
            size=size
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 