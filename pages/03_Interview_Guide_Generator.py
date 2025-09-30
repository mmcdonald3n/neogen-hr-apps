import re
from pathlib import Path
from glob import glob
import streamlit as st

from utils.branding import header, sidebar_model_controls, inject_css
from utils.llm import chat_complete
from utils.parsers import extract_text_from_upload
from utils.exporters import interview_pack_to_docx_bytes  # boxed DOCX

st.set_page_config(page_title="Interview Guide / Question Generator", page_icon="🧩", layout="wide")
inject_css()
header("Interview Guide / Question Generator")

# Sidebar model controls
model, temp, max_tokens = sidebar_model_controls()

# House style (centrally controlled)
HOUSE_STYLE_PATH = Path("house_style/NEOGEN_INTERVIEW_GUIDE_STYLE.md")
house_style_text = HOUSE_STYLE_PATH.read_text(encoding="utf-8", errors="ignore") if HOUSE_STYLE_PATH.exists() else "# Neogen Interview Guide Style\n"
st.info("Upload an optional JD and/or include seed templates. Output is a Neogen-style interview pack. House Style is centrally controlled.")

# Vendored seed templates helper + rebrand
def _load_vendor_seed_texts():
    base = Path("vendor/powerdash-ivq")
    if not base.exists():
        return []
    files = [Path(p) for p in glob(str(base / "**" / "*.md"), recursive=True)]
    return files

def _rebrand_to_neogen(text: str) -> str:
    return re.sub(r"PowerDash\s*-\s*HR|PowerDash\s*HR|Power\s*-\s*Dash|PowerDash", "Neogen", text, flags=re.IGNORECASE)

# Levels (S1–S5, M1–M6) and stages
LEVELS = ["S1","S2","S3","S4","S5","M1","M2","M3","M4","M5","M6"]
STAGES = ["1st Interview (screen / intro)","2nd Interview (functional deep-dive)","Panel Interview","Final Interview"]

DEFAULT_COMPETENCIES = [
    "Leadership & Ownership","Stakeholder Management","Execution & Delivery",
    "Problem Solving / Analytical","Communication & Influence",
    "Technical / Functional Depth","Culture & Values",
]

with st.form("ivq_form"):
    c1, c2, c3 = st.columns([2,2,2])
    with c1:
        job_title = st.text_input("Job Title*", placeholder="e.g., Senior Quality Engineer")
    with c2:
        level_code = st.selectbox("Level*", LEVELS, index=5)
    with c3:
        role_type = st.selectbox("Role Type*", ["Individual Contributor","People Manager"])

    c4, c5, c6 = st.columns([2,2,2])
    with c4:
        stage = st.selectbox("Interview Stage*", STAGES)
    with c5:
        length = st.selectbox("Interview Length", ["30 mins","45 mins","60 mins","90 mins"], index=2)
    with c6:
        tone = st.slider("Tone", 0, 10, 5, help="Plain → Formal")

    detail = st.slider("Level of Detail", 0, 10, 5, help="Concise → Comprehensive")

    comps_text = st.text_area("Key Competencies (one per line) — optional", height=120, placeholder="Leave blank to use defaults")

    c7, c8 = st.columns([2,4])
    with c7:
        jd_file = st.file_uploader("Optional: Upload JD (.docx, .pdf, .txt, .md)", type=["docx","pdf","txt","md"])
    with c8:
        seed_files = _load_vendor_seed_texts()
        seed_choices = [str(p.relative_to(Path('.'))) for p in seed_files]
        seed_selected = st.multiselect("Optional: Include seed templates (from vendored repo)", seed_choices, default=[])

    notes = st.text_area("Optional notes (team context, systems, regulatory elements, special focus areas)", height=100)

    submitted = st.form_submit_button("Generate Guide")

if submitted:
    if not job_title:
        st.error("Please provide a Job Title.")
        st.stop()

    comps = [c.strip(" •-*–\t") for c in (comps_text or "").splitlines() if c.strip()] or DEFAULT_COMPETENCIES

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
                t = Path(rel).read_text(encoding="utf-8", errors="ignore")
                parts.append(_rebrand_to_neogen(t))
            except Exception:
                pass
        seed_bundle = "\n\n".join(parts)

    def tone_label(v:int) -> str:
        return ["Plain / Direct","Plain / Direct","Plain / Direct","Professional / Neutral",
                "Professional / Neutral","Polished / Executive","Polished / Executive",
                "Polished / Executive","Formal / High-polish","Formal / High-polish","Formal / High-polish"][v]

    def detail_label(v:int) -> str:
        return ["Concise (lean)"]*4 + ["Standard (balanced)"]*3 + ["Detailed (thorough)"]*2 + ["Very Detailed (comprehensive)"]

    system = "You are an expert interviewer enablement writer. Produce interview packs that strictly follow the House Style. Use inclusive, bias-aware language and STAR-friendly prompts."

    user_prompt = f"""
HOUSE_STYLE (read-only):
{house_style_text}

CONTEXT:
- Job Title: {job_title}
- Level: {level_code}
- Role Type: {role_type}
- Interview Stage: {stage}
- Interview Length: {length}
- Competencies: {", ".join(comps)}
- Tone: {tone_label(tone)}
- Detail: {detail_label(detail)}
- Optional notes: {notes}

SEED_TEMPLATES (optional; rebranded to Neogen):
\"\"\"{(seed_bundle or "")[:20000]}\"\"\"

SOURCE_JD (optional, extracted text):
\"\"\"{(source_text or "")[:20000]}\"\"\"

REQUIREMENTS:
- Produce a complete Neogen-style interview pack in Markdown using EXACT SECTION HEADINGS in this order:
  ## Housekeeping
  ## Core Questions
  ## Competency Questions
  ## Technical Questions
  ## Culture & Values
  ## Closing Questions
  ## Close-down & Next Steps
  ## Scoring Rubric
- For each of the five “question” sections, format each question block as:
  ### {{Question text}}
  **Intent:** …
  **What good looks like:** …
  **Follow-ups:** …
- Keep concise bullet lines for Housekeeping, Close-down & Next Steps, and Scoring Rubric.
- Calibrate question depth to level {level_code} and tailor content for stage {stage}.
"""

    with st.spinner("Assembling your guide…"):
        guide_md = chat_complete(
            model,
            [{"role":"system","content":system},{"role":"user","content":user_prompt}],
            temperature=temp,
            max_tokens=max_tokens
        )

    st.markdown("### Preview (Markdown)")
    st.code(guide_md, language="markdown")

    st.download_button(
        "Download as .docx",
        data=interview_pack_to_docx_bytes(
            guide_md,
            job_title=job_title,
            interview_type="Competency",
            duration=length
        ),
        file_name=f"{job_title.replace(' ', '_')}_Interview_Pack.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
