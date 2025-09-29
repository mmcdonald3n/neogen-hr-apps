from io import BytesIO
from pathlib import Path
from typing import List
import re
import unicodedata

def _find_logo_file() -> Path | None:
    repo_root = Path(__file__).resolve().parents[1]
    search_dirs = [Path.cwd(), repo_root]
    names = ["neogen_logo", "logo"]
    exts  = [".png", ".jpg", ".jpeg", ".webp", ".gif"]
    for d in search_dirs:
        for n in names:
            for ext in exts:
                p = d / "assets" / f"{n}{ext}"
                if p.exists():
                    return p
    return None

def _find_ttf_font() -> Path | None:
    candidates = [
        Path("assets/fonts/DejaVuSans.ttf"),
        Path("assets/DejaVuSans.ttf"),
        Path(__file__).resolve().parents[1] / "assets" / "fonts" / "DejaVuSans.ttf",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None

_md_h1 = re.compile(r"^#\s+(.*)")
_md_h2 = re.compile(r"^##\s+(.*)")
_md_bullet = re.compile(r"^[-*•]\s+(.*)")

def _parse_markdown(md: str):
    lines = [ln.rstrip() for ln in md.splitlines()]
    buf: List[str] = []
    bullets: List[str] = []
    def flush_par():
        nonlocal buf
        if buf:
            yield ("p", " ".join(buf).strip())
            buf = []
    def flush_ul():
        nonlocal bullets
        if bullets:
            yield ("ul", bullets[:])
            bullets = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            for item in flush_par(): yield item
            for item in flush_ul(): yield item
            i += 1; continue
        m1 = _md_h1.match(ln)
        m2 = _md_h2.match(ln)
        mb = _md_bullet.match(ln)
        if m1:
            for item in flush_par(): yield item
            for item in flush_ul(): yield item
            yield ("h1", m1.group(1).strip())
        elif m2:
            for item in flush_par(): yield item
            for item in flush_ul(): yield item
            yield ("h2", m2.group(1).strip())
        elif mb:
            for item in flush_par(): yield item
            bullets.append(mb.group(1).strip())
        else:
            buf.append(ln.strip())
        i += 1
    for item in flush_par(): yield item
    for item in flush_ul(): yield item

# ---------------- DOCX (unchanged) ----------------
def markdown_to_docx_bytes(md: str, filename_title: str = "Job Description") -> bytes:
    from docx import Document
    from docx.shared import Inches, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()
    doc.core_properties.title = filename_title

    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    logo = _find_logo_file()
    if logo and logo.exists():
        hdr = doc.sections[0].header
        p = hdr.paragraphs[0] if hdr.paragraphs else hdr.add_paragraph()
        run = p.add_run()
        try:
            run.add_picture(str(logo), height=Inches(0.45))
        except Exception:
            pass
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    for kind, content in _parse_markdown(md):
        if kind == "h1":
            doc.add_heading(content, level=1)
        elif kind == "h2":
            doc.add_heading(content, level=2)
        elif kind == "p":
            para = doc.add_paragraph(content)
            para.paragraph_format.space_after = Pt(6)
        elif kind == "ul":
            for item in content:
                doc.add_paragraph(item, style="List Bullet")

    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# ---------------- PDF (fpdf2) with Unicode font or safe fallback ----------------
def _ascii_safe(text: str) -> str:
    # Replace common unicode punctuation with ASCII so core fonts can render
    repl = {
        "•": "-", "–": "-", "—": "-", "-": "-",  # bullets/dashes
        "“": '"', "”": '"', "„": '"', "«": '"', "»": '"',
        "’": "'", "‘": "'", "´": "'", "`": "'",
        "…": "...", "\u00A0": " ", "\u200B": "", "\u2011": "-",  # nbsp/zero-width/no-break
    }
    for k, v in repl.items():
        text = text.replace(k, v)
    # Strip diacritics then encode to latin-1
    text = unicodedata.normalize("NFKD", text)
    return text.encode("latin-1", "replace").decode("latin-1")

def markdown_to_pdf_bytes(md: str, filename_title: str = "Job Description") -> bytes:
    from fpdf import FPDF

    pdf = FPDF(unit="pt", format="A4")
    pdf.set_auto_page_break(auto=True, margin=36)
    pdf.add_page()
    left, top, right = 36, 36, 36
    pdf.set_margins(left, top, right)

    # Try Unicode TTF
    unicode_font = False
    ttf = _find_ttf_font()
    if ttf:
        try:
            pdf.add_font("DejaVu", "", str(ttf), uni=True)
            pdf.set_font("DejaVu", "", 11)
            unicode_font = True
        except Exception:
            pass
    if not unicode_font:
        pdf.set_font("Helvetica", "", 11)

    # Header logo (right)
    logo = _find_logo_file()
    if logo and logo.exists():
        try:
            pdf.image(str(logo), x=pdf.w - right - 120, y=top-6, h=36)
        except Exception:
            pass

    def write_para(text: str, size=11, style=""):
        if unicode_font:
            pdf.set_font("DejaVu", style, size)
            out = text
        else:
            pdf.set_font("Helvetica", style, size)
            out = _ascii_safe(text)
        pdf.multi_cell(w=pdf.w - left - right, h=16, txt=out)
        pdf.ln(2)

    for kind, content in _parse_markdown(md):
        if kind == "h1":
            write_para(content, size=18, style="B")
        elif kind == "h2":
            write_para(content, size=14, style="B")
        elif kind == "p":
            write_para(content, size=11)
        elif kind == "ul":
            bullet = "• " if unicode_font else "- "
            for item in content:
                write_para(bullet + item, size=11)

    out = BytesIO()
    out.write(bytes(pdf.output(dest="S")))
    return out.getvalue()
