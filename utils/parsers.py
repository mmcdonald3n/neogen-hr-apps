import io
from typing import Optional

# Optional imports: keep imports guarded so missing packages don't crash the app
try:
    from pypdf import PdfReader  # light-weight PDF text extraction
except Exception:
    PdfReader = None

try:
    from docx import Document  # python-docx
except Exception:
    Document = None


def _read_txt(data: bytes) -> str:
    try:
        return data.decode("utf-8", errors="ignore")
    except Exception:
        try:
            return data.decode("latin-1", errors="ignore")
        except Exception:
            return ""


def _read_docx(data: bytes) -> str:
    if Document is None:
        # Fallback: return empty if python-docx isn't available
        return ""
    try:
        bio = io.BytesIO(data)
        doc = Document(bio)
        return "\n".join(p.text for p in doc.paragraphs if p.text is not None)
    except Exception:
        return ""


def _read_pdf(data: bytes) -> str:
    if PdfReader is None:
        # Fallback: return empty if pypdf isn't available
        return ""
    try:
        bio = io.BytesIO(data)
        reader = PdfReader(bio)
        parts = []
        for page in reader.pages:
            try:
                txt = page.extract_text() or ""
            except Exception:
                txt = ""
            parts.append(txt)
        return "\n".join(parts)
    except Exception:
        return ""


def extract_text(uploaded_file) -> str:
    """
    Accepts a Streamlit UploadedFile and returns best-effort plain text.
    Supports: .txt, .docx, .pdf
    Returns "" on failure or unsupported types.
    """
    if not uploaded_file:
        return ""

    # Read bytes, but also put the file pointer back for any other consumer
    pos = None
    try:
        pos = uploaded_file.tell()
    except Exception:
        pass

    data = uploaded_file.read()
    try:
        uploaded_file.seek(pos or 0)
    except Exception:
        pass

    name = (getattr(uploaded_file, "name", "") or "").lower()

    if name.endswith(".pdf"):
        return _read_pdf(data)
    if name.endswith(".docx"):
        return _read_docx(data)
    if name.endswith(".txt"):
        return _read_txt(data)

    # Heuristic fallback: try text decode anyway
    return _read_txt(data)
