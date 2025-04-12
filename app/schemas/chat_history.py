from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ChatHistoryBase(BaseModel):
    chatbot_id: int
    message: str
    role: str

class ChatHistoryCreate(BaseModel):
    chatbot_id: int
    user_message: str
    assistant_response: str

class ChatHistory(ChatHistoryBase):
    id: int
    session_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class ChatHistoryResponse(BaseModel):
    messages: List[ChatHistory]

class ChatHistoryCreateResponse(BaseModel):
    user_entry: ChatHistory
    assistant_entry: ChatHistory 