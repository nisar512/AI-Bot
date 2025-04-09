from pydantic import BaseModel
from typing import Optional

class ChatbotBase(BaseModel):
    name: str
    index_id: Optional[str] = None

class ChatbotCreate(ChatbotBase):
    user_id: int

class ChatbotUpdate(ChatbotBase):
    pass

class ChatbotInDBBase(ChatbotBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class Chatbot(ChatbotInDBBase):
    pass

class ChatbotInDB(ChatbotInDBBase):
    pass 