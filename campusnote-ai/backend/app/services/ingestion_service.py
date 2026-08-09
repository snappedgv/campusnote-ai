"""
Document Ingestion Service
============================
Implements the full pipeline from Section 6:

UPLOAD -> VALIDATE -> HASH -> DUPLICATE CHECK -> EXTRACT TEXT -> CLEAN
-> CHUNK -> ADD METADATA -> EMBED -> STORE IN CHROMA -> SAVE RECORD -> DONE
"""
from pathlib import Path
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentChunk, ProcessingStatus
from app.models.subject import Subject, Unit
from app.rag.parser import extract_text
from app.rag.cleaner import clean_text
from app.rag.chunker import chunk_document
from app.rag import vectorstore
from app.utils.logger import get_logger

logger = get_logger("campusnote.ingestion")


def process_document(db: Session, document_id: str):
    """
    Runs the ingestion pipeline for an already-saved Document row
    (status=PENDING, file already written to disk). Designed to be called
    from a FastAPI BackgroundTask so upload requests return immediately.
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        logger.error(f"process_document: document {document_id} not found")
        return

    doc.processing_status = ProcessingStatus.PROCESSING
    db.commit()
    logger.info(f"Processing document {doc.id} ({doc.filename})")

    try:
        path = Path(doc.stored_path)

        # 1. EXTRACT TEXT (preserving page numbers)
        parse_result = extract_text(path, doc.file_type)
        if parse_result.needs_ocr:
            logger.info(f"Document {doc.id} looks scanned/low-text; OCR not yet implemented (TODO).")

        # 2. CLEAN TEXT (per page, preserving page numbers)
        cleaned_pages = [
            {"page": p["page"], "text": clean_text(p["text"])}
            for p in parse_result.pages
        ]

        # 3. CHUNK TEXT
        chunks = chunk_document(cleaned_pages)

        if not chunks:
            doc.processing_status = ProcessingStatus.FAILED
            doc.processing_error = (
                "No extractable text was found in this document. "
                "It may be a scanned/image-only file (OCR support is a TODO)."
            )
            doc.page_count = len(parse_result.pages)
            db.commit()
            logger.warning(f"Document {doc.id} produced zero chunks.")
            return

        # 4. ADD METADATA + 5. EMBED + 6. STORE IN CHROMA
        subject = db.query(Subject).filter(Subject.id == doc.subject_id).first() if doc.subject_id else None
        unit = db.query(Unit).filter(Unit.id == doc.unit_id).first() if doc.unit_id else None

        chroma_ids = []
        texts = []
        metadatas = []
        chunk_records = []

        for idx, chunk in enumerate(chunks):
            chroma_id = f"{doc.id}_{idx}"
            chroma_ids.append(chroma_id)
            texts.append(chunk["text"])
            metadatas.append({
                "document_id": doc.id,
                "filename": doc.filename,
                "page": chunk["page"] if chunk["page"] is not None else 0,
                "subject_id": doc.subject_id or "",
                "subject_name": subject.name if subject else "",
                "unit_id": doc.unit_id or "",
                "unit_name": unit.name if unit else "",
                "topic": doc.topic or "",
                "semester": doc.semester or "",
                "source": doc.source or "",
            })
            chunk_records.append(DocumentChunk(
                document_id=doc.id,
                chunk_index=idx,
                page_number=chunk["page"],
                text_preview=chunk["text"][:300],
                chroma_id=chroma_id,
            ))

        vectorstore.add_chunks(chroma_ids, texts, metadatas)

        # 7. SAVE DOCUMENT RECORD
        for record in chunk_records:
            db.add(record)

        doc.page_count = len(parse_result.pages)
        doc.chunk_count = len(chunks)
        doc.processing_status = ProcessingStatus.COMPLETED
        doc.processing_error = None
        from datetime import datetime
        doc.processed_at = datetime.utcnow()
        db.commit()
        logger.info(f"Document {doc.id} processed: {len(chunks)} chunks indexed.")

    except Exception as e:
        db.rollback()
        doc.processing_status = ProcessingStatus.FAILED
        doc.processing_error = str(e)
        db.commit()
        logger.error(f"Document {doc.id} processing failed: {e}")


def reindex_document(db: Session, document_id: str):
    """Deletes existing chunks (SQL + Chroma) and re-runs the pipeline.
    Used by admin 'Re-index' action, and can be called again automatically
    if the file changes (hash differs) without re-embedding unchanged files."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        return
    vectorstore.delete_document_chunks(document_id)
    db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()
    doc.chunk_count = 0
    doc.processing_status = ProcessingStatus.PENDING
    db.commit()
    process_document(db, document_id)


def delete_document(db: Session, document: Document):
    """Removes vector chunks, SQL chunk records, the file on disk, and the document row."""
    vectorstore.delete_document_chunks(document.id)
    db.query(DocumentChunk).filter(DocumentChunk.document_id == document.id).delete()
    try:
        Path(document.stored_path).unlink(missing_ok=True)
    except Exception as e:
        logger.warning(f"Could not delete file {document.stored_path}: {e}")
    db.delete(document)
    db.commit()
