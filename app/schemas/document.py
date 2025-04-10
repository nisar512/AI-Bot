from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class DocumentBase(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None

class DocumentCreate(DocumentBase):
    chatbot_id: int

class Document(DocumentBase):
    id: str
    chatbot_id: int
    created_at: datetime
    embedding: Optional[list[float]] = None

    class Config:
        from_attributes = True 