from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


class IdentifyRequest(BaseModel):
    email: Optional[str] = None
    phoneNumber: Optional[str] = None


class IdentifyResponse(BaseModel):
    primaryContactId: int
    emails: List[str]
    phoneNumbers: List[str]
    secondaryContactIds: List[int]

    class Config:
        from_attributes = True
