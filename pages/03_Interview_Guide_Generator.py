import re
import streamlit as st

# --- Branding / utils ---
from utils.branding import header, inject_css
from utils.parsers import extract_text
from utils.llm import chat_complete
from utils.exporters import markdown_to_docx_bytes

# ---------------------------------------------------------------------
# Page config must be first Streamlit call:
st.set_page_config(page_title="Interview Guide Generator", layout="centered")
inject_css()
header("Interview Guide Generator")

BUILD_INFO = "This page generates a Neogen-branded interview guide and exports to Word (.docx)."

st.caption("Consistent, fast, and high-quality HR workflows.")
st.caption(BUILD_INFO)

# ---------------------------------------------------------------------
# Tolerant wrapper for different chat_complete signatures
def _run_llm(prompt_text: str) -> str:
    try:
        return chat_complete(prompt_text, max_tokens=1800)
    except TypeError:
        try:
            return chat_complete(prompt=prompt_text, max_tokens=1800)
        except TypeError:
            msgs = [{"role": "user", "content": prompt_text}]
            return chat_complete(messages=msgs, max_tokens=1800)

def _slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "interview-guide"

LEVELS = [
    "S1 - Entry",
    "S2 - Intermediate",
    "S3 - Senior",
    "S4 - Highly Skilled",
    "S5 - Specialist",
    "M1 - Supervisor",
    "M2 - Sr Supervisor",
    "M3 - Manager",
    "M4 - Sr Manager",
    "M5 - Director",
    "M6 - Senior Director",
]

STAGES = ["First Interview", "Second Interview", "Panel Interview", "Final Interview"]
LENGTHS = ["30 mins", "45 mins", "60 mins", "90 mins"]

with st.form("ivg_form"):
    col1, col2, col3 = st.columns([1.2, 1, 1])
    with col1:
        job_title = st.text_input("Job Title*", placeholder="e.g., IT Manager")
    with col2:
        level = st.selectbox("Level", LEVELS, index=0)
    with col3:
        stage = st.selectbox("Interview Stage", STAGES, index=0)

    col4, col5 = st.columns([1, 1])
    with col4:
        length = st.selectbox("Interview Length", LENGTHS, index=2)
    with col5:
        jd_file = st.file_uploader("Upload JD (optional)", type=["pdf","docx","txt"])

    comps = st.text_area("Key Competencies (optional, one per line)", height=120,
                         placeholder="Ownership\nCollaboration\nCustomer focus")
    notes = st.text_area("Customisation Notes (optional)", height=120,
                         placeholder="Anything specific to include, tone, focus areas, etc.")
    generate = st.form_submit_button("Generate Guide")

if generate:
    if not job_title.strip():
        st.error("Please enter a Job Title.")
        st.stop()

    jd_text = ""
    if jd_file is not None:
        try:
            jd_text = extract_text(jd_file)
        except Exception as e:
            st.warning(f"Could not read the uploaded file ({e}). Continuing without it.")

    comp_list = [c.strip() for c in comps.splitlines() if c.strip()]
    comp_block = "\\n".join(f"- {c}" for c in comp_list) if comp_list else "None provided"

    prompt = f"""
You are an experienced HR interviewer at Neogen. Create a branded, structured interview guide
for the role **{job_title}** at level **{level}**, for the **{stage}** lasting **{length}**.

House style: concise, clear English, inclusive language; no jargon. Use headings and bullets.

If the job description text below is present, use it as the source of truth; otherwise use best practice.
Only include content that would be appropriate for {stage.lower()}.

Job description (may be empty):
\"\"\"{jd_text}\"\"\"

Key competencies (optional):
{comp_block}

Customisation notes (optional):
{notes}

Required output (Markdown):

# Interview Agenda
- Welcome & introductions (2–3 minutes)
- Role overview & context (brief)
- Structured question blocks (by competency or topic)
- Candidate questions
- Close & next steps

# Interview Questions
For each topic/competency include:
- **Purpose** (what we’re testing)
- **Primary question**
- **2–3 probing prompts**
- **What good looks like** (scoring anchors 1–5: Poor, Needs Improvement, Satisfactory, Very Good, Excellent)

# Practical / Scenario (optional)
One short scenario aligned to the role; include expected signals.

# Evaluation Criteria
- A short rubric for 1–5 across the main areas.

# Closing Script
Brief, warm closing that thanks the candidate, explains next steps and timelines, and who to contact for questions.
"""

    with st.spinner("Generating interview guide…"):
        guide_md = _run_llm(prompt)

    st.success("Guide generated.")
    st.markdown(guide_md)

    # Show a copy button (Streamlit code block provides a copy icon)
    with st.expander("Copy the Markdown"):
        st.code(guide_md, language="markdown")

    # Export to DOCX
    try:
        docx_bytes = markdown_to_docx_bytes(guide_md, filename_title=job_title)
    except TypeError:
        # Fallback if exporter signature differs on this branch
        docx_bytes = markdown_to_docx_bytes(guide_md)

    file_name = f"{_slugify(job_title)}-interview-guide.docx"
    st.download_button(
        "Download as .docx",
        data=docx_bytes,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary",
    )

# === NEOGEN BOXED DOCX DOWNLOAD (auto added) ===
try:
    if 'guide_md' in locals() and isinstance(guide_md, str) and guide_md.strip():
        from utils.exporters import interview_pack_to_docx_bytes
        job_name = job_title if 'job_title' in locals() else "Role"
        lvl      = level if 'level' in locals() else ""
        stg      = stage if 'stage' in locals() else ""
        dur      = duration if 'duration' in locals() else ""
        docx_bytes = interview_pack_to_docx_bytes(
            guide_md=guide_md,
            title="Interview Guide",
            job_title=job_name,
            level=lvl,
            stage=stg,
            duration=dur,
            logo_path="assets/neogen_logo.png",
        )
        st.download_button(
            "Download as .docx",
            data=docx_bytes,
            file_name=f"{job_name.replace(' ','_')}_Interview_Guide.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
except Exception as _e:
    pass
# === END NEOGEN BOXED DOCX DOWNLOAD ===
