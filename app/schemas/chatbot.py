from pydantic import BaseModel
from typing import Optional

class ChatbotBase(BaseModel):
    name: str

class ChatbotCreate(ChatbotBase):
    user_id: int

class ChatbotUpdate(ChatbotBase):
    index_id: Optional[str] = None

class ChatbotInDBBase(ChatbotBase):
    id: int
    user_id: int
    index_id: Optional[str] = None

    class Config:
        from_attributes = True

class Chatbot(ChatbotInDBBase):
    pass

class ChatbotInDB(ChatbotInDBBase):
    pass 