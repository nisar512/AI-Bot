from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class DocumentBase(BaseModel):
    chatbot_id: int
    metadata: Optional[Dict[str, Any]] = None

class DocumentCreate(DocumentBase):
    content: str

class Document(DocumentBase):
    id: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True 