import streamlit as st
from pathlib import Path
from glob import glob
import re
from utils.branding import header, sidebar_model_controls, inject_css
from utils.llm import chat_complete
from utils.parsers import extract_text_from_upload
from utils.exporters import markdown_to_docx_bytes

st.set_page_config(page_title="Interview Guide / Question Generator", page_icon="🧩", layout="wide")
inject_css()
header("Interview Guide / Question Generator")

# Sidebar model controls
model, temp, max_tokens = sidebar_model_controls()

# Read-only Neogen house style
HOUSE_STYLE_PATH = Path("house_style/NEOGEN_INTERVIEW_GUIDE_STYLE.md")
house_style_text = HOUSE_STYLE_PATH.read_text(encoding="utf-8", errors="ignore") if HOUSE_STYLE_PATH.exists() else "# Neogen Interview Guide Style\n"
st.info("Upload an optional JD and/or include seed templates. Output is a Neogen-style interview guide with competency questions, probes, and a scoring rubric. House Style is centrally controlled.")

# Vendored seed templates helper + rebrand
def _load_vendor_seed_texts():
    base = Path("vendor/powerdash-ivq")
    if not base.exists():
        return []
    files = [Path(p) for p in glob(str(base / '**' / '*.md'), recursive=True)]
    return files

def _rebrand_to_neogen(text: str) -> str:
    text = re.sub(r'PowerDash\s*-?\s*HR', 'Neogen', text, flags=re.IGNORECASE)
    text = re.sub(r'Power\s*-?\s*Dash',  'Neogen', text, flags=re.IGNORECASE)
    text = re.sub(r'PowerDash',         'Neogen', text, flags=re.IGNORECASE)
    return text

# Fixed Neogen levels (S1–S5, M1–M6)
LEVELS = ["S1","S2","S3","S4","S5","M1","M2","M3","M4","M5","M6"]
STAGES = [
    "1st Interview (screen / intro)",
    "2nd Interview (functional deep-dive)",
    "Panel Interview",
    "Final Interview",
]
DEFAULT_COMPETENCIES = [
    "Leadership & Ownership",
    "Stakeholder Management",
    "Execution & Delivery",
    "Problem Solving / Analytical",
    "Communication & Influence",
    "Technical / Functional Depth",
    "Culture & Values",
]

with st.form("ivq_form"):
    c1, c2, c3 = st.columns([2,2,2])
    with c1:
        job_title = st.text_input("Job Title*", placeholder="e.g., Senior Quality Engineer")
    with c2:
        level_code = st.selectbox("Level*", LEVELS, index=5)  # default M1-ish
    with c3:
        role_type = st.selectbox("Role Type*", ["Individual Contributor", "People Manager"])

    c4, c5, c6 = st.columns([2,2,2])
    with c4:
        stage = st.selectbox("Interview Stage*", STAGES)
    with c5:
        tone = st.slider("Tone", 0, 10, 5, help="Plain → Formal")
    with c6:
        detail = st.slider("Level of Detail", 0, 10, 5, help="Concise → Comprehensive")

    comps_text = st.text_area("Key Competencies (one per line) — optional", height=120, placeholder="Leave blank to use defaults")

    c7, c8 = st.columns([2,4])
    with c7:
        jd_file = st.file_uploader("Optional: Upload JD (.docx, .pdf, .txt, .md)", type=["docx","pdf","txt","md"])
    with c8:
        seed_files = _load_vendor_seed_texts()
        seed_choices = [str(p.relative_to(Path('.'))) for p in seed_files]
        seed_selected = st.multiselect("Optional: Include seed templates (from vendored repo)", seed_choices, default=[])

    notes = st.text_area("Optional notes (team context, systems, regulatory elements, special focus areas)", height=120, placeholder="Leave blank if not needed.")
    submitted = st.form_submit_button("Generate Guide")

if submitted:
    if not job_title:
        st.error("Please provide a Job Title.")
        st.stop()

    comps = [c.strip(' •-*–\t') for c in (comps_text or '').splitlines() if c.strip()]
    if not comps:
        comps = DEFAULT_COMPETENCIES

    source_text = ""
    if jd_file is not None:
        try:
            source_text = extract_text_from_upload(jd_file)
        except Exception:
            source_text = ""

    seed_bundle = ""
    if seed_selected:
        parts = []
        for rel in seed_selected:
            try:
                t = Path(rel).read_text(encoding='utf-8', errors='ignore')
                parts.append(_rebrand_to_neogen(t))
            except Exception:
                pass
        seed_bundle = "\n\n".join(parts)

    def tone_label(v:int) -> str:
        if v <= 2: return "Plain / Direct"
        if v <= 4: return "Professional / Neutral"
        if v <= 7: return "Polished / Executive"
        return "Formal / High-polish"

    def detail_label(v:int) -> str:
        if v <= 3: return "Concise (lean)"
        if v <= 6: return "Standard (balanced)"
        if v <= 8: return "Detailed (thorough)"
        return "Very Detailed (comprehensive)"

    system = "You are an expert interviewer enablement writer. Produce interview guides that strictly follow the House Style. Use inclusive, bias-aware language and STAR-friendly prompts."
    user_prompt = f"""
HOUSE_STYLE (read-only):
{house_style_text}

CONTEXT:
- Job Title: {job_title}
- Level: {level_code}
- Role Type: {role_type}
- Interview Stage: {stage}
- Competencies: {", ".join(comps)}
- Tone: {tone_label(tone)} (slider={tone})
- Detail: {detail_label(detail)} (slider={detail})
- Optional notes: {notes}

SEED_TEMPLATES (optional; rebranded to Neogen):
\"\"\"{(seed_bundle or "")[:20000]}\"\"\"

SOURCE_JD (optional, extracted text):
\"\"\"{(source_text or "")[:20000]}\"\"\"

REQUIREMENTS:
- Produce a complete Neogen-style interview guide in Markdown.
- **Stage tailoring**:
  * 1st Interview: high-level fit, motivation, role understanding, basic competencies; shorter question sets; ensure inclusive, welcoming tone.
  * 2nd Interview: functional / technical deep-dive; require more evidence, complexity, and measurable outcomes.
  * Panel Interview: cross-functional scenarios, stakeholder alignment, conflict/negotiation; emphasise breadth and collaboration.
  * Final Interview: values alignment, long-term impact, leadership maturity, risk judgement; ensure questions distinguish top-tier candidates.
- Include:
  1) At-a-glance overview
  2) Interview structure (stages, durations, assessors, what to probe)
  3) For each competency: 4–8 behavioural questions (escalate depth appropriately for {level_code}) + probing follow-ups
  4) Role-type extras: if People Manager, leadership/coaching/performance/hiring/org health; if IC, depth/autonomy/impact
  5) A clear 1–5 evaluation rubric with behavioural anchors per competency
- Match UK/US spelling to location if implied; avoid internal system names unless vital.
"""
    with st.spinner("Assembling your guide…"):
        guide_md = chat_complete(
            model,
            [{"role":"system","content":system},{"role":"user","content":user_prompt}],
            temperature=temp,
            max_tokens=max_tokens
        )

    st.markdown("### Output")
    st.code(guide_md, language="markdown")  # built-in copy button

    st.download_button(
        "Download as .docx",
        data=markdown_to_docx_bytes(guide_md, filename_title=job_title + " – Interview Guide"),
        file_name=f"{job_title.replace(' ', '_')}_Interview_Guide.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
