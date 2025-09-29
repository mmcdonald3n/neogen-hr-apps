from io import BytesIO
from pathlib import Path
from typing import List
import re

# --------- Logo discovery (same logic as branding) ----------
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
    # svg not supported in python-docx; skip for exporters
    return None

# --------- Simple Markdown splitter (H1/H2, paragraphs, bullets) ----------
_md_h1 = re.compile(r"^#\s+(.*)")
_md_h2 = re.compile(r"^##\s+(.*)")
_md_bullet = re.compile(r"^[-*•]\s+(.*)")

def _parse_markdown(md: str):
    """Yield ('h1'|'h2'|'p'|'ul', text or [items]) preserving simple structure."""
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
            # blank
            for item in flush_par(): yield item
            for item in flush_ul(): yield item
            i += 1
            continue
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

# --------- DOCX (python-docx) ----------
def markdown_to_docx_bytes(md: str, filename_title: str = "Job Description") -> bytes:
    from docx import Document
    from docx.shared import Inches, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()
    doc.core_properties.title = filename_title

    # Base font
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    # Header with logo (right aligned)
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

# --------- PDF (ReportLab) ----------
def markdown_to_pdf_bytes(md: str, filename_title: str = "Job Description") -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, ListFlowable, ListItem
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_RIGHT
    from reportlab.lib.units import inch

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36,
                            title=filename_title)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="H1", parent=styles["Heading1"], spaceAfter=6))
    styles.add(ParagraphStyle(name="H2", parent=styles["Heading2"], spaceAfter=6))
    styles.add(ParagraphStyle(name="Body", parent=styles["BodyText"], spaceAfter=6))
    styles.add(ParagraphStyle(name="LogoRight", parent=styles["Normal"], alignment=TA_RIGHT))

    flow = []

    # Logo in header (right)
    logo = _find_logo_file()
    if logo and logo.exists():
        try:
            img = Image(str(logo), height=0.45*inch, width=None)
            img.hAlign = "RIGHT"
            flow += [img, Spacer(1, 8)]
        except Exception:
            pass

    # Content
    for kind, content in _parse_markdown(md):
        if kind == "h1":
            flow.append(Paragraph(content, styles["H1"]))
        elif kind == "h2":
            flow.append(Paragraph(content, styles["H2"]))
        elif kind == "p":
            flow.append(Paragraph(content, styles["Body"]))
        elif kind == "ul":
            items = [ListItem(Paragraph(it, styles["Body"])) for it in content]
            flow.append(ListFlowable(items, bulletType="bullet", leftIndent=18))

    doc.build(flow)
    return buf.getvalue()
