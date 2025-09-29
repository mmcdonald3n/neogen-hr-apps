from pathlib import Path
from typing import Optional
from io import BytesIO

def _safe_decode(b: bytes) -> str:
    try:
        return b.decode("utf-8")
    except Exception:
        return b.decode("latin-1", errors="ignore")

def extract_text_from_upload(file) -> str:
    """
    Accepts a Streamlit UploadedFile and returns best-effort plain text
    for .docx, .pdf, .txt, .md. Falls back to UTF-8/Latin-1 decode.
    """
    name = (file.name or "").lower()
    data = file.read()
    # Put the cursor back so callers can re-read if needed
    try:
        file.seek(0)
    except Exception:
        pass

    if name.endswith(".txt") or name.endswith(".md"):
        return _safe_decode(data)

    if name.endswith(".docx"):
        try:
            from docx import Document
            bio = BytesIO(data)
            doc = Document(bio)
            parts = []
            for p in doc.paragraphs:
                txt = (p.text or "").strip()
                if txt:
                    parts.append(txt)
            return "\n".join(parts).strip()
        except Exception:
            return _safe_decode(data)

    if name.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            bio = BytesIO(data)
            reader = PdfReader(bio)
            chunks = []
            for page in reader.pages:
                txt = page.extract_text() or ""
                if txt.strip():
                    chunks.append(txt)
            return "\n\n".join(chunks).strip()
        except Exception:
            return _safe_decode(data)

    # Fallback
    return _safe_decode(data)
