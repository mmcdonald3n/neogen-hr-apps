import streamlit as st
from utils.branding import header, sidebar_model_controls, inject_css
from utils.llm import chat_complete
from utils.parsers import extract_text
from pathlib import Path

st.set_page_config(page_title="Job Advert Generator", page_icon="📢", layout="wide")
inject_css()
header("Job Advert Generator")

model, temp, max_tokens = sidebar_model_controls()

with st.expander("House Style Source"):
    default_style = Path("house_style/NEOGEN_HOUSE_STYLE_ADVERT.md").read_text(encoding="utf-8")
    style_override = st.text_area("Advert House Style (Markdown)", value=default_style, height=200)

with st.form("ad_form"):
    c1, c2 = st.columns(2)
    with c1:
        job_title = st.text_input("Job Title*", "")
        location = st.text_input("Location*", "Remote/Hybrid/Onsite")
    with c2:
        salary_notes = st.text_input("Compensation Notes", "Competitive + benefits")
        apply_link = st.text_input("Apply Link / CTA", "https://careers.neogen.com")

    jd_file = st.file_uploader("Upload JD (docx/pdf/txt)", type=["docx","pdf","txt"])
    extra_opts = st.text_area("Extra Options (team, tech, travel, reporting line)", "")
    submitted = st.form_submit_button("Generate Advert")

if submitted:
    jd_text = extract_text(jd_file) if jd_file else ""
    system = "You write concise, compelling job adverts in Neogen style."
    prompt = f"""
HOUSE_STYLE_ADVERT:
{style_override}

JOB_TITLE: {job_title}
LOCATION: {location}
COMPENSATION: {salary_notes}
APPLY_LINK: {apply_link}

SOURCE_JD:
{jd_text}

EXTRA_OPTIONS:
{extra_opts}

OUTPUT: A polished job advert in Markdown, with strong hook, clear sections, inclusive language, and a bold call-to-action.
"""
    with st.spinner("Generating Advert..."):
        out = chat_complete(model, [{"role":"system","content":system},{"role":"user","content":prompt}], temperature=temp, max_tokens=max_tokens)
    st.markdown("### Output")
    st.download_button("Download as .md", data=out.encode("utf-8"), file_name=f"{job_title or 'role'}_Advert.md", mime="text/markdown")
    st.markdown(out)
