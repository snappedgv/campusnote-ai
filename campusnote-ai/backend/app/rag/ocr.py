"""
OCR module (TODO - not implemented yet).

Section 25 of the spec requires the pipeline to be designed so OCR can be
added later for scanned PDFs that yield little/no extractable text.

To implement:
    1. Add `pytesseract` + `pillow` (or a cloud OCR API) to requirements.txt
    2. Rasterize each PDF page to an image (PyMuPDF: page.get_pixmap())
    3. Run OCR on the image to get text
    4. Return the same ParseResult shape as app.rag.parser so the rest of
       the ingestion pipeline (cleaner -> chunker -> embeddings) needs no
       changes.

This stub keeps the integration point explicit without pulling in the
extra OCR dependencies by default.
"""
from pathlib import Path
from app.rag.parser import ParseResult


def ocr_pdf(path: Path) -> ParseResult:
    raise NotImplementedError(
        "OCR is not yet implemented. This is a TODO extension point — see "
        "module docstring in app/rag/ocr.py for the integration plan."
    )
