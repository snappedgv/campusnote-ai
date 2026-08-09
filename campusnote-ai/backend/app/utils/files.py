"""
File validation, secure filenames, and SHA-256 hashing utilities.
"""
import hashlib
import re
import uuid
from pathlib import Path

ALLOWED_EXTENSIONS = {"pdf", "docx", "pptx", "txt"}


def get_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def is_allowed_file(filename: str) -> bool:
    return get_extension(filename) in ALLOWED_EXTENSIONS


def secure_filename(filename: str) -> str:
    """Strips directory components and unsafe characters, prefixes a UUID
    to avoid collisions/overwrites."""
    name = Path(filename).name
    name = re.sub(r"[^A-Za-z0-9_.\-]", "_", name)
    return f"{uuid.uuid4().hex}_{name}"


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()
