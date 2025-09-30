import streamlit as st
from utils.branding import header, sidebar_model_controls, inject_css
from utils.llm import chat_complete
from utils.parsers import extract_text_from_upload

st.set_page_config(page_title="Interview Guide Generator", page_icon="📋", layout="wide")
inject_css()
header("Interview Guide Generator")

model, temp, max_tokens = sidebar_model_controls()

with st.form("ivg_form"):
    c1, c2, c3 = st.columns(3)
    with c1:
        job_title = st.text_input("Job Title*", "")
    with c2:
        seniority = st.selectbox("Seniority", ["Associate","Specialist","Senior","Manager","Sr Manager","Director","VP"])
    with c3:
        duration = st.selectbox("Interview Length", ["30 mins","45 mins","60 mins","90 mins"], index=2)

    jd_file = st.file_uploader("Upload JD (optional)", type=["docx","pdf","txt"])
    key_competencies = st.text_area("Key Competencies (one per line)", "Ownership\nCollaboration\nCustomer Focus\nTechnical depth")
    custom_notes = st.text_area("Customisation Notes", "Any specific areas to probe or avoid")

    submitted = st.form_submit_button("Generate Interview Guide")

if submitted:
    jd_text = extract_text_from_upload(jd_file) if jd_file else ""
    system = "You produce structured interview guides with sections, suggested timings, and evaluation rubrics."
    user = f"""
JOB_TITLE: {job_title}
SENIORITY: {seniority}
DURATION: {duration}

KEY_COMPETENCIES:
{key_competencies}

JD_CONTEXT (optional):
{jd_text}

CUSTOM_NOTES:
{custom_notes}

OUTPUT: A structured guide with:
- Opening script
- Section timings
- Behavioral & technical questions mapped to competencies
- Score rubric (1–5) and red flags
- Closing & next steps
Format in Markdown, concise and practical.
"""
    with st.spinner("Generating Guide..."):
        out = chat_complete(model, [{"role":"system","content":system},{"role":"user","content":user}], temperature=temp, max_tokens=max_tokens)
    st.markdown("### Output")
    st.download_button("Download as .md", data=out.encode("utf-8"), file_name=f"{job_title or 'role'}_Interview_Guide.md", mime="text/markdown")
    st.markdown(out)

