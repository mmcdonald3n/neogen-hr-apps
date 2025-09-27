import streamlit as st
from utils.branding import header, sidebar_model_controls, inject_css
from utils.llm import chat_complete
from utils.parsers import extract_text

st.set_page_config(page_title="Interview Question Generator", page_icon="❓", layout="wide")
inject_css()
header("Interview Question Generator")

model, temp, max_tokens = sidebar_model_controls()

with st.form("ivq_form"):
    c1, c2 = st.columns(2)
    with c1:
        job_title = st.text_input("Job Title*", "")
        seniority = st.selectbox("Level", ["Associate","Specialist","Senior","Manager","Sr Manager","Director","VP"])
    with c2:
        focus = st.multiselect("Focus Areas", ["Behavioral","Technical","Leadership","Culture & Values","Scenario/Case"], default=["Behavioral","Technical"])

    jd_file = st.file_uploader("Upload JD (optional)", type=["docx","pdf","txt"])
    custom = st.text_area("Custom Requirements", "Add any domain specifics, systems, methods, or metrics to target.")

    submitted = st.form_submit_button("Generate Questions")

if submitted:
    jd_text = extract_text(jd_file) if jd_file else ""
    system = "You write sharp, bias-aware interview questions with sample strong/weak answers and scoring."
    prompt = f"""
JOB_TITLE: {job_title}
SENIORITY: {seniority}
FOCUS_AREAS: {", ".join(focus)}

JD_CONTEXT:
{jd_text}

CUSTOM:
{custom}

OUTPUT: For each focus area, provide:
- 5 targeted questions
- What good looks like (bullet points)
- Pitfalls/red flags
- Score rubric 1–5
Format as Markdown with clear headings.
"""
    with st.spinner("Generating Questions..."):
        out = chat_complete(model, [{"role":"system","content":system},{"role":"user","content":prompt}], temperature=temp, max_tokens=max_tokens)
    st.markdown("### Output")
    st.download_button("Download as .md", data=out.encode("utf-8"), file_name=f"{job_title or 'role'}_Interview_Questions.md", mime="text/markdown")
    st.markdown(out)
