import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.database import Base


class ProcessingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    stored_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # pdf, docx, pptx, txt

    subject_id = Column(String, ForeignKey("subjects.id"), nullable=True)
    unit_id = Column(String, ForeignKey("units.id"), nullable=True)
    topic = Column(String, nullable=True)

    department = Column(String, nullable=True)
    semester = Column(String, nullable=True)
    academic_year = Column(String, nullable=True)
    faculty = Column(String, nullable=True)
    source = Column(String, nullable=True)  # e.g. "LMS", "Manual Upload"

    file_hash = Column(String, nullable=False, index=True)
    processing_status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING)
    processing_error = Column(Text, nullable=True)
    page_count = Column(Integer, nullable=True)
    chunk_count = Column(Integer, default=0)

    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

    subject = relationship("Subject", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    """
    Metadata record mirroring what is stored in ChromaDB, kept in SQL too
    so the admin dashboard can inspect ingestion without querying the vector
    store directly.
    """
    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=True)
    text_preview = Column(Text, nullable=True)  # first ~300 chars for admin UI
    chroma_id = Column(String, nullable=False)  # id used in the vector collection

    document = relationship("Document", back_populates="chunks")
