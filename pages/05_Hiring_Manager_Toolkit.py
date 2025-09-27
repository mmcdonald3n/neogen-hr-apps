import streamlit as st
from utils.branding import header, sidebar_model_controls, inject_css
from utils.llm import chat_complete

st.set_page_config(page_title="Hiring Manager Toolkit", page_icon="🧰", layout="wide")
inject_css()
header("Hiring Manager Toolkit")

model, temp, max_tokens = sidebar_model_controls()

with st.form("hmt_form"):
    job_title = st.text_input("Job Title*", "")
    region = st.text_input("Region", "USA / EMEA / LATAM / APAC")
    stack  = st.text_input("Systems Stack", "Workday, Teams, Calendly, Docusign, Vetting Providers")
    notes  = st.text_area("Notes (team, stages, approvals, offer process)", "")
    submitted = st.form_submit_button("Generate Toolkit (Placeholder content OK)")

if submitted:
    system = "You produce pragmatic hiring toolkits: playbook, onboarding checklist, roles & expectations."
    prompt = f"""
Create a Hiring Manager Toolkit for: {job_title}
Region: {region}
Systems: {stack}

Notes:
{notes}

Deliver:
1) Hiring Manager Playbook (stages, SLAs, anti-bias guidance, decision criteria)
2) IT Onboarding Instructions (systems access, hardware, timeline)
3) Expectations of all parties (HM, TA, Interviewers, Candidate)
Short, bullet-led, Markdown.
"""
    with st.spinner("Generating Toolkit..."):
        out = chat_complete(model, [{"role":"system","content":system},{"role":"user","content":prompt}], temperature=temp, max_tokens=max_tokens)
    st.markdown("### Output")
    st.download_button("Download as .md", data=out.encode("utf-8"), file_name=f"{job_title or 'role'}_Hiring_Manager_Toolkit.md", mime="text/markdown")
    st.markdown(out)
