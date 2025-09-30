import streamlit as st

from utils.branding import header, inject_css
from utils.llm import chat_complete
from utils.parsers import extract_text
try:
    from utils.exporters import markdown_to_docx_bytes
except Exception:
    markdown_to_docx_bytes = None  # exporter fallback

st.set_page_config(page_title="Interview Guide Generator", layout="wide")
inject_css()
header("Interview Guide Generator")

with st.form("ivg_form"):
    col1, col2, col3 = st.columns([2,1,1])
    with col1:
        job_title = st.text_input("Job Title*", "")
    with col2:
        level = st.selectbox("Level", ["S1","S2","S3","S4","S5","S6","M1","M2","M3","M4","M5","M6"], index=0)
    with col3:
        stage = st.selectbox("Interview Stage", ["1st Interview","2nd Interview","Panel Interview","Final Interview"])

    jd_file = st.file_uploader("Upload JD (optional)", type=["docx","pdf","txt"])
    competencies = st.text_area("Key Competencies (optional, one per line)")
    notes = st.text_area("Customisation Notes (optional)")
    submitted = st.form_submit_button("Generate Guide")

if submitted:
    if not job_title.strip():
        st.warning("Please enter a Job Title.")
        st.stop()

    jd_text = ""
    if jd_file is not None:
        try:
            jd_text = extract_text(jd_file)
        except Exception:
            jd_text = ""

    # Build the system-style prompt (single string)
    prompt = f"""
You are preparing a NEOGEN-branded interview guide in HOUSE STYLE (clear, friendly, practical; UK spelling).
Create the guide **IN MARKDOWN** using the sections and formatting below. Keep bullets tight, avoid waffle.

Context
- Job Title: {job_title}
- Level: {level}
- Interview Stage: {stage}
- Optional Competencies (one per line):
{competencies}

- Extra Notes:
{notes}

- Relevant JD text (optional, may be empty):
{jd_text}

Output structure (exact section headings):
# Interview Plan
- Opening (2–3 sentences)
- Role Overview (3–5 bullets)
- Stage Focus for {stage} (3–5 bullets tailored to this stage)
- Technical / Functional Questions (8–12 bullets)
- Behavioural Questions (6–8 bullets) — include STAR prompts
- Scenario or Case Prompt (1 prompt tailored to {job_title})
- Assessment & Scoring
  - Provide a 1–5 rubric for each of these competencies (if any were provided). If none provided, use: Leadership & Team Management; Technical Proficiency; Strategic Thinking; Communication Skills.
  - Format rubric bullets like: **Competency Name:** 1–5 scale description.
- Closing Script
  - Thank the candidate, explain next steps (“we aim to be in touch within a week”), and invite questions.

Formatting rules
- Use H1/H2/H3 and bullets; no tables.
- Keep each question to one bullet; no numbering.
- Keep the Closing Script as a short paragraph.
"""

    # LLM call (always pass a single string)
    guide_md = chat_complete(prompt, max_tokens=1800)
    guide_md_text = "\n\n".join(guide_md) if isinstance(guide_md, (list,tuple)) else str(guide_md)

    st.markdown(guide_md_text)

    # DOCX export (boxed/house-style done by our exporter)
    if markdown_to_docx_bytes is not None:
        try:
            docx_bytes = markdown_to_docx_bytes(guide_md_text, filename_title=job_title or "Interview Guide")
            st.download_button(
                "Download as .docx",
                data=docx_bytes,
                file_name=f"{(job_title or 'Interview_Guide').replace(' ','_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        except Exception as e:
            st.info("DOCX export unavailable. You can still copy the Markdown below.")

    with st.expander("Copy the Markdown"):
        st.code(guide_md_text, language="markdown")
