import streamlit as st
from utils.branding import header, sidebar_model_controls, inject_css
from utils.llm import chat_complete
from pathlib import Path
import pandas as pd

st.set_page_config(page_title="Job Description Generator", page_icon="📝", layout="wide")
inject_css()
header("Job Description Generator")

model, temp, max_tokens = sidebar_model_controls()

with st.expander("House Style Source"):
    st.write("Defaulting to **house_style/NEOGEN_HOUSE_STYLE_JD.md**. You can paste or upload your own below.")
    default_style = Path("house_style/NEOGEN_HOUSE_STYLE_JD.md").read_text(encoding="utf-8")
    style_override = st.text_area("House Style (Markdown)", value=default_style, height=220)

levels_file = Path("house_style/JOB_LEVELS.csv")
levels_df = pd.read_csv(levels_file) if levels_file.exists() else pd.DataFrame({"Level":["L1","L2"],"Name":["Associate","Specialist"],"Descriptor":["Entry","IC"]})
level_display = levels_df.apply(lambda r: f"{r['Level']} - {r['Name']}: {r['Descriptor']}", axis=1).tolist()

with st.form("jd_form"):
    c1, c2, c3 = st.columns(3)
    with c1:
        job_title = st.text_input("Job Title*", "")
        department = st.text_input("Department/Function*", "")
    with c2:
        location = st.text_input("Location*", "Remote/Hybrid/Onsite")
        work_pattern = st.text_input("Work Pattern", "Full-time")
    with c3:
        level_choice = st.selectbox("Level", level_display, index=2 if len(level_display)>2 else 0)
        travel = st.text_input("Travel", "Occasional")

    role_purpose = st.text_area("Role Purpose (1–3 short paragraphs)")
    key_resps = st.text_area("Key Responsibilities (bullets, one per line)")
    req_quals = st.text_area("Required Qualifications (bullets, one per line)")
    pref_quals = st.text_area("Preferred Qualifications (bullets, one per line)")
    comps     = st.text_area("Competencies (bullets, one per line)")

    submitted = st.form_submit_button("Generate JD")

if submitted:
    system = "You are an HR content generator. Output in clean Markdown following the given House Style and Neogen tone."
    lvl = level_choice.split(" - ")[0] if " - " in level_choice else level_choice
    user_prompt = f"""
HOUSE_STYLE:
{style_override}

INSTRUCTIONS:
- Create a Job Description in Neogen House Style.
- Job Title: {job_title}
- Department/Function: {department}
- Location: {location}
- Work Pattern: {work_pattern}
- Level: {lvl}
- Travel: {travel}

CONTENT:
Role Purpose:
{role_purpose}

Key Responsibilities:
{key_resps}

Required Qualifications:
{req_quals}

Preferred Qualifications:
{pref_quals}

Competencies:
{comps}

FORMAT: Use clear headings, bullet lists, and concise, inclusive language.
"""
    with st.spinner("Generating JD..."):
        out = chat_complete(model, [{"role":"system","content":system},{"role":"user","content":user_prompt}], temperature=temp, max_tokens=max_tokens)
    st.markdown("### Output")
    st.download_button("Download as .md", data=out.encode("utf-8"), file_name=f"{job_title or 'job'}_JD.md", mime="text/markdown")
    st.markdown(out)
