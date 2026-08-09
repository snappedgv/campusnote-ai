"""
Document Parser
================
Extracts text from PDF, DOCX, PPTX and TXT files while preserving
page/slide numbers, since the chatbot must cite the source page.

Returns a list of dicts: [{"page": int, "text": str}, ...]

Section 25 (scanned PDF support): if a PDF page yields (almost) no
extractable text, it is flagged in `needs_ocr` so the ingestion service
can report it. OCR itself is left as a modular TODO (see ocr.py stub)
so it can be plugged in later without changing the pipeline shape.
"""
from pathlib import Path
from typing import List, Dict

import fitz  # PyMuPDF
from docx import Document as DocxDocument
from pptx import Presentation


class ParseResult:
    def __init__(self, pages: List[Dict], needs_ocr: bool = False):
        self.pages = pages          # [{"page": int, "text": str}]
        self.needs_ocr = needs_ocr  # True if extracted text looks empty (scanned doc)


def parse_pdf(path: Path) -> ParseResult:
    pages = []
    total_chars = 0
    doc = fitz.open(str(path))
    try:
        for i, page in enumerate(doc, start=1):
            text = page.get_text("text") or ""
            total_chars += len(text.strip())
            pages.append({"page": i, "text": text})
    finally:
        doc.close()
    needs_ocr = total_chars < 20 * max(len(pages), 1)  # heuristic: near-empty extraction
    return ParseResult(pages=pages, needs_ocr=needs_ocr)


def parse_docx(path: Path) -> ParseResult:
    """DOCX has no native page concept until rendered, so we treat the
    whole document as a single logical 'page' (page=1). Paragraph-level
    granularity is preserved via double-newlines for chunking."""
    doc = DocxDocument(str(path))
    parts = []
    for para in doc.paragraphs:
        if para.text.strip():
            parts.append(para.text)
    # also pull table content
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
            if row_text:
                parts.append(row_text)
    text = "\n\n".join(parts)
    return ParseResult(pages=[{"page": 1, "text": text}], needs_ocr=len(text.strip()) < 20)


def parse_pptx(path: Path) -> ParseResult:
    """Each slide is treated as one 'page' so citations can say 'Slide N'."""
    prs = Presentation(str(path))
    pages = []
    for i, slide in enumerate(prs.slides, start=1):
        texts = []
        for shape in slide.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    line = "".join(run.text for run in para.runs)
                    if line.strip():
                        texts.append(line)
            if shape.has_table:
                for row in shape.table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                    if row_text:
                        texts.append(row_text)
        pages.append({"page": i, "text": "\n".join(texts)})
    total_chars = sum(len(p["text"].strip()) for p in pages)
    return ParseResult(pages=pages, needs_ocr=total_chars < 10 * max(len(pages), 1))


def parse_txt(path: Path) -> ParseResult:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return ParseResult(pages=[{"page": 1, "text": text}], needs_ocr=False)


PARSERS = {
    "pdf": parse_pdf,
    "docx": parse_docx,
    "pptx": parse_pptx,
    "txt": parse_txt,
}


def extract_text(path: Path, file_type: str) -> ParseResult:
    parser = PARSERS.get(file_type.lower())
    if parser is None:
        raise ValueError(f"Unsupported file type: {file_type}")
    return parser(path)
