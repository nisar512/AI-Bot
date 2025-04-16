from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SessionWithFirstMessage(BaseModel):
    id: str
    chatbot_id: int
    chatbot_name: str
    created_at: datetime
    updated_at: Optional[datetime]
    first_message: Optional[str]

class SessionList(BaseModel):
    sessions: list[SessionWithFirstMessage] 