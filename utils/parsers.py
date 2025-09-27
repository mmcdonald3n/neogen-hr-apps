from typing import Optional
from io import BytesIO
from pathlib import Path

def extract_text(uploaded_file) -> str:
    """
    Accepts Streamlit UploadedFile for .txt, .docx, .pdf
    """
    if uploaded_file is None:
        return ""
    name = uploaded_file.name.lower()
    data = uploaded_file.read()

    if name.endswith(".txt"):
        try:
            return data.decode("utf-8", errors="ignore")
        except Exception:
            return data.decode("latin-1", errors="ignore")

    if name.endswith(".docx"):
        from docx import Document
        f = BytesIO(data)
        doc = Document(f)
        return "\n".join([p.text for p in doc.paragraphs])

    if name.endswith(".pdf"):
        from pypdf import PdfReader
        f = BytesIO(data)
        reader = PdfReader(f)
        text = []
        for page in reader.pages:
            text.append(page.extract_text() or "")
        return "\n".join(text)

    # Fallback to best-effort decode
    try:
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return str(data)
