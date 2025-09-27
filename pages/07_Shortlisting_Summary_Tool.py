import streamlit as st
from utils.branding import header, sidebar_model_controls, inject_css
from utils.llm import chat_complete
from utils.parsers import extract_text

st.set_page_config(page_title="Shortlisting Summary Tool", page_icon="🧮", layout="wide")
inject_css()
header("Shortlisting Summary Tool")

model, temp, max_tokens = sidebar_model_controls()

st.write("Upload up to five CVs and a JD to produce an executive summary and comparison.")

with st.form("shortlist_form"):
    jd = st.file_uploader("Job Description (docx/pdf/txt)*", type=["docx","pdf","txt"])
    c1, c2 = st.columns(2)
    with c1:
        cv1 = st.file_uploader("CV #1", type=["docx","pdf","txt"])
        cv2 = st.file_uploader("CV #2", type=["docx","pdf","txt"])
        cv3 = st.file_uploader("CV #3", type=["docx","pdf","txt"])
    with c2:
        cv4 = st.file_uploader("CV #4", type=["docx","pdf","txt"])
        cv5 = st.file_uploader("CV #5", type=["docx","pdf","txt"])

    extra = st.text_area("Focus Areas (optional)", "Industry experience; Years in role; Key technologies; Leadership; Regulatory; Travel; Salary fit")
    submitted = st.form_submit_button("Generate Summary")

if submitted:
    if not jd:
        st.error("Please upload a JD.")
        st.stop()

    jd_text = extract_text(jd)
    cvs = [cv1, cv2, cv3, cv4, cv5]
    cv_texts = [extract_text(f) for f in cvs if f is not None]

    if not cv_texts:
        st.error("Please upload at least one CV.")
        st.stop()

    system = "You are an expert TA partner generating concise, decision-ready shortlists."
    prompt = f"""
JOB_DESCRIPTION:
{jd_text}

CANDIDATE_CVS:
{"\n\n---\n\n".join(cv_texts)}

FOCUS_AREAS:
{extra}

OUTPUT:
1) Executive Summary (5-8 bullet points)
2) Comparison Table (CSV-friendly): Candidate, Strengths, Risks/Gaps, Years Experience, Key Skills, Notable Companies, Salary/Level Fit (guess), Overall Rating (1-5)
3) Recommendation: Who to proceed with and why
Tone: crisp, neutral, evidence-based. Keep table compact.
"""
    with st.spinner("Analysing candidates vs role..."):
        out = chat_complete(model, [{"role":"system","content":system},{"role":"user","content":prompt}], temperature=temp, max_tokens=max_tokens)

    st.markdown("### Output")
    st.download_button("Download as .md", data=out.encode("utf-8"), file_name="Shortlist_Summary.md", mime="text/markdown")
    st.markdown(out)
