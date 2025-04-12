from pydantic import BaseModel, validator
from datetime import datetime, timezone
from typing import Optional

class AccessKeyBase(BaseModel):
    chatbot_id: int
    expires_at: Optional[datetime] = None

    @validator('expires_at')
    def ensure_timezone_aware(cls, v):
        if v is not None and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

class AccessKeyCreate(AccessKeyBase):
    pass

class AccessKey(AccessKeyBase):
    id: int
    key: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True 