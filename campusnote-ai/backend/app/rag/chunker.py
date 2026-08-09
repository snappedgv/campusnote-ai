"""
Chunker
=======
Splits cleaned page text into overlapping chunks suitable for embedding.
Chunk size and overlap are configurable via .env (CHUNK_SIZE, CHUNK_OVERLAP).

We split on paragraph/sentence boundaries where possible instead of
blindly cutting at N characters, so a chunk doesn't get sliced mid-sentence
whenever avoidable. Each chunk retains the page number it came from so the
answer can cite "Document.pdf — Page 12".
"""
import re
from typing import List, Dict
from app.config import settings

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def _split_into_sentences(paragraph: str) -> List[str]:
    return [s for s in SENTENCE_SPLIT_RE.split(paragraph) if s.strip()]


def chunk_page_text(page_number: int, text: str, chunk_size: int = None, overlap: int = None) -> List[Dict]:
    """Returns [{"page": int, "text": str}]"""
    chunk_size = chunk_size or settings.CHUNK_SIZE
    overlap = overlap or settings.CHUNK_OVERLAP

    if not text or not text.strip():
        return []

    paragraphs = [p for p in text.split("\n\n") if p.strip()]
    sentences: List[str] = []
    for para in paragraphs:
        sentences.extend(_split_into_sentences(para))
        sentences.append("\n\n")  # paragraph boundary marker

    chunks = []
    current = ""
    for sent in sentences:
        if sent == "\n\n":
            continue
        candidate = (current + " " + sent).strip() if current else sent
        if len(candidate) > chunk_size and current:
            chunks.append(current.strip())
            # start new chunk with overlap taken from the tail of the previous chunk
            overlap_text = current[-overlap:] if overlap > 0 else ""
            current = (overlap_text + " " + sent).strip()
        else:
            current = candidate

    if current.strip():
        chunks.append(current.strip())

    # Fallback: if a single sentence exceeds chunk_size, hard-split it
    final_chunks = []
    for c in chunks:
        if len(c) <= chunk_size * 1.5:
            final_chunks.append(c)
        else:
            for i in range(0, len(c), chunk_size - overlap):
                piece = c[i:i + chunk_size]
                if piece.strip():
                    final_chunks.append(piece.strip())

    return [{"page": page_number, "text": c} for c in final_chunks if len(c.strip()) > 10]


def chunk_document(pages: List[Dict]) -> List[Dict]:
    """pages: [{"page": int, "text": str}] (already cleaned) -> flat list of chunks"""
    all_chunks = []
    for page in pages:
        all_chunks.extend(chunk_page_text(page["page"], page["text"]))
    return all_chunks
