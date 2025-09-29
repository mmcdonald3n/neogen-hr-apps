from io import BytesIO
from pathlib import Path
from typing import List
import re

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

def markdown_to_docx_bytes(md: str, filename_title: str = "Job Description") -> bytes:
    from docx import Document
    from docx.shared import Inches, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from io import BytesIO

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

def markdown_to_pdf_bytes(md: str, filename_title: str = "Job Description") -> bytes:
    # PDF using pure-Python fpdf2 (works on Python 3.13)
    from fpdf import FPDF
    from io import BytesIO

    pdf = FPDF(unit="pt", format="A4")
    pdf.set_auto_page_break(auto=True, margin=36)
    pdf.add_page()
    left, top, right = 36, 36, 36
    pdf.set_margins(left, top, right)

    logo = _find_logo_file()
    if logo and logo.exists():
        try:
            pdf.image(str(logo), x=pdf.w - right - 120, y=top-6, h=36)
        except Exception:
            pass

    def write_para(text: str, size=11, style=""):
        pdf.set_font("Helvetica", style, size)
        pdf.multi_cell(w=pdf.w - left - right, h=16, txt=text)
        pdf.ln(2)

    for kind, content in _parse_markdown(md):
        if kind == "h1":
            write_para(content, size=18, style="B")
        elif kind == "h2":
            write_para(content, size=14, style="B")
        elif kind == "p":
            write_para(content, size=11)
        elif kind == "ul":
            for item in content:
                write_para("• " + item, size=11)

    out = BytesIO()
    out.write(bytes(pdf.output(dest="S")))
    return out.getvalue()
