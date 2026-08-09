from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class BookmarkCreate(BaseModel):
    message_id: Optional[str] = None
    question: str
    answer: str
    subject_name: Optional[str] = None
    unit_name: Optional[str] = None
    sources: Optional[List[dict]] = None


class BookmarkOut(BaseModel):
    id: str
    question: str
    answer: str
    subject_name: Optional[str] = None
    unit_name: Optional[str] = None
    sources: Optional[List[dict]] = None
    created_at: datetime

    class Config:
        from_attributes = True
