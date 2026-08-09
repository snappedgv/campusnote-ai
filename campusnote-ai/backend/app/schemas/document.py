from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.document import ProcessingStatus


class DocumentOut(BaseModel):
    id: str
    filename: str
    file_type: str
    subject_id: Optional[str] = None
    unit_id: Optional[str] = None
    topic: Optional[str] = None
    department: Optional[str] = None
    semester: Optional[str] = None
    academic_year: Optional[str] = None
    faculty: Optional[str] = None
    source: Optional[str] = None
    processing_status: ProcessingStatus
    processing_error: Optional[str] = None
    page_count: Optional[int] = None
    chunk_count: int = 0
    uploaded_at: datetime

    class Config:
        from_attributes = True
