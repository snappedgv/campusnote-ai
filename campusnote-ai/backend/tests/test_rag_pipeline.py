from pathlib import Path
import hashlib
from app.rag.cleaner import clean_text
from app.rag.chunker import chunk_page_text, chunk_document
from app.rag.question_type import detect_question_type
from app.utils.files import sha256_of_file, is_allowed_file, secure_filename


def test_clean_text_collapses_whitespace():
    dirty = "Hello   world.\n\n\n\nThis is   a test.\n12\n"
    cleaned = clean_text(dirty)
    assert "   " not in cleaned
    assert "\n\n\n" not in cleaned


def test_chunker_respects_chunk_size():
    text = "This is a sentence. " * 200  # long text
    chunks = chunk_page_text(page_number=1, text=text, chunk_size=200, overlap=20)
    assert len(chunks) > 1
    for c in chunks:
        assert len(c["text"]) <= 400  # generous upper bound incl. fallback splitting
        assert c["page"] == 1


def test_chunk_document_empty_pages_produce_no_chunks():
    chunks = chunk_document([{"page": 1, "text": ""}])
    assert chunks == []


def test_question_type_detection():
    assert detect_question_type("What is normalization?") == "definition"
    assert detect_question_type("Explain the process of deadlock avoidance.") == "explain"
    assert detect_question_type("Differentiate between TCP and UDP.") == "difference"
    assert detect_question_type("Write the algorithm for quicksort.") == "algorithm"
    assert detect_question_type("What are the advantages and disadvantages of RAID?") == "advantages_disadvantages"
    assert detect_question_type("Write a program to implement BFS.") == "programming"


def test_sha256_hash_and_duplicate_detection(tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("identical content")
    f2.write_text("identical content")
    assert sha256_of_file(f1) == sha256_of_file(f2)

    f3 = tmp_path / "c.txt"
    f3.write_text("different content")
    assert sha256_of_file(f1) != sha256_of_file(f3)


def test_allowed_file_types():
    assert is_allowed_file("notes.pdf")
    assert is_allowed_file("notes.docx")
    assert is_allowed_file("notes.pptx")
    assert is_allowed_file("notes.txt")
    assert not is_allowed_file("notes.exe")
    assert not is_allowed_file("notes")


def test_secure_filename_strips_path_traversal():
    name = secure_filename("../../etc/passwd")
    assert "/" not in name
    assert ".." not in name.replace("_", "")
