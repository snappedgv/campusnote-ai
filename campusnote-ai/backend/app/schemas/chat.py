from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SourceOut(BaseModel):
    document: str
    document_id: Optional[str] = None
    page: Optional[int] = None
    unit: Optional[str] = None
    relevance: float
    excerpt: str


class ChatRequest(BaseModel):
    chat_id: Optional[str] = None  # None => create a new chat
    question: str
    subject_id: Optional[str] = None
    unit_id: Optional[str] = None
    topic: Optional[str] = None
    exam_type: Optional[str] = None  # CAT 1, CAT 2, Semester
    marks: Optional[int] = None  # 2,5,10,13,15
    mode: str = "college_notes"  # "college_notes" strictly grounded, "general" fallback (still disclosed)


class ChatResponse(BaseModel):
    chat_id: str
    message_id: str
    answer: str
    question_type: str
    marks: Optional[int] = None
    sources: List[SourceOut] = []
    grounded: bool


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    question_type: Optional[str] = None
    marks: Optional[int] = None
    grounded: bool
    sources: Optional[list] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatOut(BaseModel):
    id: str
    title: str
    subject_id: Optional[str] = None
    unit_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: List[MessageOut] = []

    class Config:
        from_attributes = True


class ChatSummaryOut(BaseModel):
    id: str
    title: str
    subject_id: Optional[str] = None
    unit_id: Optional[str] = None
    updated_at: datetime

    class Config:
        from_attributes = True
