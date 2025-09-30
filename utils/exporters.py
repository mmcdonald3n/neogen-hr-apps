# utils/exporters.py
from io import BytesIO
from pathlib import Path
from typing import List, Dict, Tuple
from docx import Document
from docx.oxml.ns import qn
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement

NEOGEN_GREEN = RGBColor(0x00, 0x67, 0x47)   # brand-ish green
PALE_MINT    = RGBColor(0xE6, 0xF2, 0xEF)   # light background for headings

def _set_cell_shading(cell, rgb: RGBColor | None = None):
    """Fill cell with solid color."""
    if rgb is None:
        return
    tc = cell._tc
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), f'{rgb.rgb:06x}')
    tc.get_or_add_tcPr().append(shd)

def _set_cell_borders(cell):
    """Thin borders all around."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    borders = OxmlElement('w:tcBorders')
    for edge in ("top", "left", "bottom", "right"):
        tag = OxmlElement(f"w:{edge}")
        tag.set(qn('w:val'), 'single')
        tag.set(qn('w:sz'), '8')       # ~0.5pt
        tag.set(qn('w:space'), '0')
        tag.set(qn('w:color'), 'A6A6A6')
        borders.append(tag)
    tcPr.append(borders)

def _para(p, text, bold=False, size=11, color: RGBColor | None = None):
    r = p.add_run(text)
    r.bold = bold
    r.font.size = Pt(size)
    if color:
        r.font.color.rgb = color

def _section_heading(doc: Document, text: str):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(13)
    run.font.color.rgb = NEOGEN_GREEN

def _add_header(doc: Document, job_title: str, stage: str, level: str, length: str, logo_path: Path):
    # Title row with logo on the right
    t = doc.add_table(rows=1, cols=2)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.columns[0].width = Inches(5.6)
    t.columns[1].width = Inches(1.8)

    left = t.cell(0, 0).paragraphs[0]
    _para(left, f"Interview Guide — {job_title}", bold=True, size=18)
    left.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT

    # logo
    if logo_path and logo_path.exists():
        right = t.cell(0, 1).paragraphs[0]
        right.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
        try:
            right.add_run().add_picture(str(logo_path), width=Inches(1.3))
        except Exception:
            pass

    # Meta row
    m = doc.add_table(rows=1, cols=3)
    m.alignment = WD_TABLE_ALIGNMENT.CENTER
    for c in range(3):
        _set_cell_borders(m.cell(0, c))
    _set_cell_shading(m.cell(0, 0), PALE_MINT)
    _set_cell_shading(m.cell(0, 1), PALE_MINT)
    _set_cell_shading(m.cell(0, 2), PALE_MINT)
    m.cell(0, 0).paragraphs[0].add_run(f"Stage: {stage}").bold = True
    m.cell(0, 1).paragraphs[0].add_run(f"Level: {level}").bold = True
    m.cell(0, 2).paragraphs[0].add_run(f"Duration: {length}").bold = True

def _question_box(doc: Document, q: str, intent: str, good: str, followups: List[str]):
    """
    Two-column table:
      left  = question + intent + what good looks like + follow-ups
      right = large NOTES box (empty)
    """
    table = doc.add_table(rows=5, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.columns[0].width = Inches(5.2)
    table.columns[1].width = Inches(2.7)

    # Row 0: "Question" header spanning both columns (visual anchor)
    hdr = table.cell(0, 0)
    hdr.merge(table.cell(0, 1))
    _set_cell_borders(hdr)
    _set_cell_shading(hdr, PALE_MINT)
    ph = hdr.paragraphs[0]
    _para(ph, "Question", bold=True)

    # Row 1: actual question + "NOTES" title in right
    _set_cell_borders(table.cell(1, 0)); _set_cell_borders(table.cell(1, 1))
    _para(table.cell(1, 0).paragraphs[0], q, size=11)
    notes_hdr = table.cell(1, 1).paragraphs[0]
    _para(notes_hdr, "NOTES", bold=True)

    # Row 2: Intent
    _set_cell_borders(table.cell(2, 0)); _set_cell_borders(table.cell(2, 1))
    _set_cell_shading(table.cell(2, 0), PALE_MINT)
    _para(table.cell(2, 0).paragraphs[0], "Intent", bold=True)
    _para(table.cell(2, 1).paragraphs[0], "")

    # Row 3: Intent text (span left col)
    _set_cell_borders(table.cell(3, 0)); _set_cell_borders(table.cell(3, 1))
    _para(table.cell(3, 0).paragraphs[0], intent)
    _para(table.cell(3, 1).paragraphs[0], "")

    # Row 4: What good looks like + follow-ups (stacked)
    # Make a nested table in left cell for neat labels
    left = table.cell(4, 0)
    _set_cell_borders(left); _set_cell_borders(table.cell(4, 1))
    inner = left.add_table(rows=2, cols=1)
    _set_cell_shading(inner.cell(0, 0), PALE_MINT)
    _para(inner.cell(0, 0).paragraphs[0], "What good looks like", bold=True)
    _para(inner.cell(1, 0).paragraphs[0], good)

    # Follow-ups list (beneath)
    p = left.add_paragraph()
    _para(p, "Follow-ups", bold=True)
    for f in followups:
        left.add_paragraph(f"• {f}")

    # give some breathing room after each box
    doc.add_paragraph()

def _parse_questions(md: str) -> Tuple[List[Dict], Dict]:
    """
    Very forgiving parser that looks for blocks shaped like:

    Question text

    Intent:
    ...

    What good looks like:
    ...

    Follow-ups:
    - one
    - two
    """
    blocks = []
    current = {}
    lines = [ln.rstrip() for ln in md.splitlines()]
    buf = []

    def flush():
        nonlocal current, buf
        if not buf:
            return
        # First non-empty line = question
        q = ""
        for ln in buf:
            if ln.strip():
                q = ln.strip().strip("•- ")
                break
        intent = _extract_section(buf, "Intent")
        good   = _extract_section(buf, "What good looks like")
        fol    = _extract_list(buf,  "Follow-ups")
        if q:
            blocks.append({"q": q, "intent": intent, "good": good, "followups": fol})
        buf = []
        current = {}

    def _starts_heading(ln: str) -> bool:
        return ln.startswith("#")

    def _extract_section(buf: List[str], name: str) -> str:
        start = None
        for i, ln in enumerate(buf):
            if ln.lower().startswith(name.lower()):
                start = i + 1
                break
        if start is None: return ""
        out = []
        for j in range(start, len(buf)):
            t = buf[j].strip()
            if t.endswith(":") and t[:-1].lower() in ("intent","what good looks like","follow-ups"):
                break
            out.append(buf[j])
        return "\n".join(out).strip()

    def _extract_list(buf: List[str], name: str) -> List[str]:
        start = None
        for i, ln in enumerate(buf):
            if ln.lower().startswith(name.lower()):
                start = i + 1
                break
        if start is None: return []
        out = []
        for j in range(start, len(buf)):
            t = buf[j].strip()
            if t and (t[0] in "-•"):
                out.append(t[1:].strip())
            elif t == "":
                continue
            else:
                # stop when next label or paragraph appears
                if t.endswith(":"): break
        return out

    for ln in lines:
        if _starts_heading(ln):
            # section break; flush any buffered block
            flush()
            continue
        # blank line delimiting questions
        if ln.strip() == "" and buf and buf[-1].strip() == "":
            flush()
        else:
            buf.append(ln)
    flush()
    meta = {}
    return blocks, meta

def interview_pack_to_docx_bytes(
    guide_md: str,
    job_title: str,
    stage: str,
    level: str,
    length: str,
    logo_path: str = "assets/neogen_logo.png",
) -> bytes:
    """
    Create a Neogen-branded interview pack (.docx) with boxed sections and a notes column.
    """
    doc = Document()
    # base fonts
    style = doc.styles["Normal"].font
    style.name = "Calibri"
    style.size = Pt(11)

    _add_header(doc, job_title, stage, level, length, Path(logo_path))

    # Sections we care about will be parsed into boxes
    questions, _ = _parse_questions(guide_md)

    # Optional Housekeeping or other guidance that might appear at the top of md
    _section_heading(doc, "Housekeeping")
    doc.add_paragraph("• Welcome & introductions")
    doc.add_paragraph("• Outline agenda and timings")
    doc.add_paragraph("• Consent for interview and note-taking")
    doc.add_paragraph("• DEI commitment & confidentiality")
    doc.add_paragraph()

    # Questions boxes
    _section_heading(doc, "Interview Questions")
    for blk in questions:
        _question_box(
            doc,
            q=blk.get("q","").strip(),
            intent=blk.get("intent",""),
            good=blk.get("good",""),
            followups=blk.get("followups", []),
        )

    # Close-down & Next Steps — always present
    _section_heading(doc, "Close-down & Next Steps")
    doc.add_paragraph("• Thank the candidate for their time and participation.")
    doc.add_paragraph("• Explain next steps in the process and expected timelines.")
    doc.add_paragraph("• Confirm who will contact them and how feedback will be shared.")
    doc.add_paragraph("• Invite any final questions and close the interview professionally.")

    # Scoring rubric (simple footer)
    _section_heading(doc, "Scoring Rubric")
    doc.add_paragraph("5 – Excellent | 4 – Very Good | 3 – Satisfactory | 2 – Needs Improvement | 1 – Poor")

    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()
# --- Back-compat alias so existing imports keep working ---
def markdown_to_docx_bytes(guide_md, job_title, stage, level, length, logo_path):
    """Alias to support older imports; forwards to interview_pack_to_docx_bytes."""
    return interview_pack_to_docx_bytes(
        guide_md=guide_md,
        job_title=job_title,
        stage=stage,
        level=level,
        length=length,
        logo_path=logo_path,
    )
