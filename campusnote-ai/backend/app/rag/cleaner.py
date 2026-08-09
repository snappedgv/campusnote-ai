"""
Text Cleaner
============
Normalizes extracted text before chunking: collapses whitespace, strips
common PDF artifacts (page-footer repeats, form-feed chars), and removes
control characters, while preserving sentence/paragraph structure and
important terminology (we do NOT lowercase or strip punctuation, since
exam terminology must be preserved verbatim).
"""
import re


def clean_text(text: str) -> str:
    if not text:
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove non-printable / control characters (keep newlines and tabs)
    text = re.sub(r"[^\x09\x0A\x20-\x7E\u00A0-\uFFFF]", " ", text)

    # Collapse 3+ blank lines into a max of 2 (paragraph break)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Collapse runs of spaces/tabs
    text = re.sub(r"[ \t]{2,}", " ", text)

    # Trim trailing whitespace on each line
    text = "\n".join(line.strip() for line in text.split("\n"))

    # Remove stray page-number-only lines like "12" or "Page 12"
    text = re.sub(r"(?im)^\s*(page\s*)?\d{1,4}\s*$", "", text)

    return text.strip()
