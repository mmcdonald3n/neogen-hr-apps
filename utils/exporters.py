import io
from typing import Iterable, Optional

try:
    from docx import Document
    from docx.shared import Pt, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
except Exception:
    Document = None  # will be handled gracefully


# ---------------------------
# Low-level helpers
# ---------------------------

def _add_logo(doc, logo_path: Optional[str]):
    if not logo_path:
        return
    try:
        header = doc.sections[0].header
        p = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
        run = p.add_run()
        run.add_picture(logo_path, width=Inches(1.25))
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    except Exception:
        pass


def _set_table_borders(table):
    # Give the table a visible 1pt border (looks like a "box")
    try:
        tbl = table._element
        tblPr = tbl.tblPr or tbl._new_tblPr()
        borders = OxmlElement("w:tblBorders")
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            el = OxmlElement(f"w:{edge}")
            el.set(qn("w:val"), "single")
            el.set(qn("w:sz"), "8")   # 8 = 0.5pt; looks tidy
            el.set(qn("w:space"), "0")
            el.set(qn("w:color"), "auto")
            borders.append(el)
        tblPr.append(borders)
    except Exception:
        pass


def _add_box(doc, title: str, lines: Iterable[str]):
    # One-cell table with borders = a nice "box"
    table = doc.add_table(rows=1, cols=1)
    _set_table_borders(table)
    cell = table.rows[0].cells[0]
    # Title
    p = cell.paragraphs[0]
    run = p.add_run(title)
    run.bold = True
    run.font.size = Pt(11)
    # Body
    for ln in lines:
        p = cell.add_paragraph(ln)
        p.paragraph_format.space_after = Pt(4)
    doc.add_paragraph("")  # small spacer after each box


def _add_heading(doc, text: str, level: int = 0):
    try:
        if level == 0:
            p = doc.add_paragraph()
            r = p.add_run(text)
            r.bold = True
            r.font.size = Pt(18)
        else:
            doc.add_heading(text, level=level)
    except Exception:
        doc.add_paragraph(text)


def _add_md_block_as_paragraphs(doc, md: str):
    """
    Super-light MD to DOCX: supports # headings and -/* bullets. Everything else becomes a paragraph.
    """
    for raw in (md or "").splitlines():
        line = raw.rstrip()
        if not line:
            doc.add_paragraph("")
            continue
        # Heading
        if line.startswith("#"):
            hashes = len(line) - len(line.lstrip("#"))
            text = line.lstrip("# ").strip()
            lvl = min(max(hashes, 1), 4)
            _add_heading(doc, text, level=lvl)
            continue
        # Bullet
        if line.lstrip().startswith(("-", "*")):
            text = line.lstrip("-* ").strip()
            p = doc.add_paragraph(text, style="List Bullet")
            p.paragraph_format.space_after = Pt(2)
            continue
        # Normal para
        p = doc.add_paragraph(line)
        p.paragraph_format.space_after = Pt(4)


# ---------------------------
# Public exporters
# ---------------------------

def markdown_to_docx_bytes(md: str, filename_title: str = "", logo_path: Optional[str] = None) -> bytes:
    """
    Simple, dependable MD -> DOCX. Returns document bytes.
    """
    if Document is None:
        # Fail soft if python-docx not available
        return b""

    doc = Document()
    _add_logo(doc, logo_path)
    if filename_title:
        _add_heading(doc, filename_title, level=0)
    _add_md_block_as_paragraphs(doc, md)

    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()


def interview_pack_to_docx_bytes(
    guide_md: str,
    competencies_md: str,
    rubric_md: str,
    interview_type: str,
    job_title: str,
    duration: str = "",
    logo_path: Optional[str] = None,
) -> bytes:
    """
    Build a 'boxed' Interview Guide with Neogen branding vibes.
    Each section goes in a bordered single-cell table.
    """
    if Document is None:
        return b""

    doc = Document()
    _add_logo(doc, logo_path)

    # Main title
    title = f"Interview Guide – {job_title}".strip(" –")
    _add_heading(doc, title, level=0)

    # Overview box
    overview_lines = []
    if interview_type:
        overview_lines.append(f"**Interview Stage:** {interview_type}")
    if duration:
        overview_lines.append(f"**Duration:** {duration}")
    _add_box(doc, "Interview Overview", overview_lines or ["See details below."])

    # Competencies box
    comp_lines = [ln for ln in (competencies_md or "").splitlines() if ln.strip()]
    _add_box(doc, "Key Competencies", comp_lines or ["(None specified)"])

    # Questions box (from guide_md)
    # Turn markdown into lines (keeps bullets looking nice in the box)
    q_lines = [ln for ln in (guide_md or "").splitlines()]
    _add_box(doc, "Interview Questions", q_lines or ["(No questions generated)"])

    # Scoring rubric box
    rubric_lines = [ln for ln in (rubric_md or "").splitlines()]
    _add_box(doc, "Scoring Rubric", rubric_lines or [
        "1 – Poor   | 2 – Fair   | 3 – Good   | 4 – Very Good   | 5 – Excellent"
    ])

    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()
