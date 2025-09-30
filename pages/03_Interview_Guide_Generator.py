import streamlit as st
try:
    from utils.branding import header
except Exception:
    # Fallback so the app runs even if branding.header isn't present
    def header(text: str):
        import streamlit as st
        st.header(text)
try:
    from utils.branding import inject_css
except Exception:
    # Fallback: minimal top padding so the header doesn't overlap
    def inject_css():
        import streamlit as st
try:
    from utils.branding import header
except Exception:
    # Fallback so the app runs even if branding.header isn't present
    def header(text: str):
        import streamlit as st
        st.header(text)
        st.markdown(
            "<style>.main > div:first-child{padding-top:1rem}</style>",
            unsafe_allow_html=True
        )
from utils.exporters import interview_pack_to_docx_bytes as markdown_to_docx_bytes
from utils.parsers import extract_text
from utils.llm import chat_complete
from utils.exporters import markdown_to_docx_bytes
from utils.exporters import interview_pack_to_docx_bytes
def _run_llm(prompt_text: str) -> str:
    \"\"\"Be tolerant to different chat_complete signatures across branches.\"\"\"
    try:
        # most branches: chat_complete(prompt, max_tokens=...)
        return chat_complete(prompt_text, max_tokens=1800)
    except TypeError:
        try:
            # some wrappers: chat_complete(prompt=..., max_tokens=...)
            return chat_complete(prompt=prompt_text, max_tokens=1800)
        except TypeError:
            # message-style: chat_complete(messages=[...], max_tokens=...)
            msgs = [ { "role": "user", "content": prompt_text } ]
            return chat_complete(messages=msgs, max_tokens=1800)


st.set_page_config(page_title="Interview Guide Generator", layout="wide")
inject_css()
header("Interview Guide Generator")

# --- Controls ---
with st.form("ivg_form"):
    col1, col2, col3 = st.columns([1.2,1,1])
    with col1:
        job_title = st.text_input("Job Title*", placeholder="e.g., IT Manager")
        level = st.selectbox(
            "Level",
            ["S1 - Entry", "S2 - Intermediate", "S3 - Senior", "S4 - Highly Skilled",
             "S5 - Specialist", "M1 - Supervisor", "M2 - Sr Supervisor", "M3 - Manager",
             "M4 - Sr Manager", "M5 - Director", "M6 - Senior Director"],
            index=2
        )
    with col2:
        stage = st.selectbox("Interview Stage", ["1st Interview", "2nd Interview", "Panel Interview", "Final Interview"], index=0)
        length = st.selectbox("Interview Length", ["30 mins","45 mins","60 mins","90 mins"], index=2)
    with col3:
        tone = st.slider("Tone (professional ↔ friendly)", 0, 10, 5)
        detail = st.slider("Detail (concise ↔ thorough)", 0, 10, 5)

    jd_file = st.file_uploader("Upload JD (optional)", type=["pdf","docx","txt"])
    competencies = st.text_area("Key Competencies (optional, one per line)", help="Leave blank if you want the model to infer from the JD/title.")
    notes = st.text_area("Customisation Notes (optional)")

    submitted = st.form_submit_button("Generate Guide")

def _read_jd(file):
    if not file: 
        return ""
    try:
        return extract_text(file)
    except Exception:
        return ""

if submitted:
    if not job_title.strip():
        st.warning("Please enter a Job Title.")
        st.stop()

    jd_text = _read_jd(jd_file)
    comp_lines = [c.strip() for c in competencies.splitlines() if c.strip()]
    comp_block = "\\n".join(f"- {c}" for c in comp_lines) if comp_lines else "(Model to infer key competencies from JD/title.)"

    prompt = f'''
You are an expert HR interviewer. Create a structured **Interview Guide** for the role **{job_title}** at Neogen.

Context:
- Level: {level}
- Stage: {stage}
- Interview length: {length}
- Tone scale (0-10): {tone}
- Detail scale (0-10): {detail}
- Key Competencies (if any):
{comp_block}

Job Description (if provided):
\"\"\"{jd_text[:8000]}\"\"\"  # truncated for safety

Output as well-structured **Markdown** with these sections and anchors:
# Interview Guide — {job_title}
## Overview
- Purpose of this interview stage
- What good looks like at {level} for this role
- Interview logistics (duration {length}, panel guidance if applicable)

## Competency Questions
Provide 6–10 competency-based questions aligned to competencies for this role.
For each question include:
- **Question**
- **What to listen for** (bullets)
- **Scoring rubric (1–5)** with concise behavioral anchors

## Role/Technical Questions
Provide 4–8 role-specific questions with the same sub-structure as above.

## Candidate Questions
3–5 thoughtful questions the candidate might ask.

## Closing & Next Steps
- How to wrap the interview
- What to tell the candidate about next steps

Keep wording concise, inclusive, and plain-English. Avoid jargon.
'''

    with st.spinner("Creating guide..."):
        guide_md = _run_llm(prompt)

    docx_bytes = interview_pack_to_docx_bytes(
    guide_md=guide_md,
    job_title=job_title or "Role",
    stage=stage,          # e.g. "1st Interview"
    level=level,          # e.g. "S1".."M6"
    length=length,        # e.g. "60 mins"
    logo_path="assets/neogen_logo.png",
)

st.download_button(
    "Download as .docx",
    data=docx_bytes,
    file_name=f"{job_title.replace(' ','_')}_Interview_Pack.docx",
    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
)





