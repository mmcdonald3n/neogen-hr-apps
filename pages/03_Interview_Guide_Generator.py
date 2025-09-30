import streamlit as st

from utils.branding import header, inject_css
from utils.llm import chat_complete
from utils.parsers import extract_text
from utils.exporters import markdown_to_docx_bytes

st.set_page_config(page_title="Interview Guide Generator", layout="wide")

inject_css()
header("Interview Guide Generator")

with st.form("ivg_form"):
    job_title = st.text_input("Job Title*", "")
    jd_file = st.file_uploader("Upload JD (optional)", type=["docx", "pdf", "txt"])
    competencies = st.text_area("Key Competencies (optional, one per line)")
    notes = st.text_area("Customisation Notes (optional)")
    submitted = st.form_submit_button("Generate Guide")

if submitted:
    # Pull JD text if a file was uploaded (safe if None)
    jd_text = ""
    if jd_file is not None:
        try:
            jd_text = extract_text(jd_file)
        except Exception:
            jd_text = ""

    prompt = f"""
You are an experienced Neogen interviewer. Produce a concise, professional interview guide IN MARKDOWN with these sections:
# Interview Plan
- Opening (1 short paragraph)
- Role Overview (bullet list of 3–5)
- Technical/Functional Questions (8–12)
- Behavioural Questions (6–8) using STAR prompts
- Scoring rubric (1–5) for each competency listed
- Closing Script (thank, next steps, invitation to ask questions)

Job Title: {job_title}
Core Competencies (optional, one per line):
{competencies}

Additional Notes (optional):
{notes}

Relevant Job Description Text (optional):
{jd_text}

House style: clear, friendly, practical; UK spelling; keep bullets tight.
"""

    # Run the model robustly; ensure we pass a single string
    guide_md = chat_complete(prompt, max_tokens=1800)

    # Render the markdown for on-screen view
    st.markdown(guide_md)

    # Prepare safe text and DOCX export
    guide_md_text = "\n\n".join(guide_md) if isinstance(guide_md, (list, tuple)) else str(guide_md)
    docx_bytes = markdown_to_docx_bytes(guide_md_text, filename_title=job_title or "Interview Guide")

    st.download_button(
        "Download as .docx",
        data=docx_bytes,
        file_name=f"{(job_title or 'Interview_Guide').replace(' ', '_')}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

    with st.expander("Copy the Markdown"):
        st.code(guide_md_text, language="markdown")
