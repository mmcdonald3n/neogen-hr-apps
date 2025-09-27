import streamlit as st
from utils.branding import header, inject_css
from pathlib import Path

st.set_page_config(page_title="Neogen HR Apps", page_icon="✅", layout="wide")
inject_css()

header("HR Apps", kicker="Neogen HR Suite")

st.write("Welcome! Choose a tool below.")

# Tiles
with st.container():
    st.markdown('<div class="tile-grid">', unsafe_allow_html=True)

    # 6 top tiles
    tiles = [
        ("01_Job_Description_Generator.py", "Job Description Generator", "Produce Neogen house-style JDs from options."),
        ("02_Job_Advert_Generator.py", "Job Advert Generator", "Convert JD + options into a branded advert."),
        ("03_Interview_Guide_Generator.py", "Interview Guide Generator", "Structured interview guide templates."),
        ("04_Interview_Question_Generator.py", "Interview Question Generator", "Tailored questions + scoring rubrics."),
        ("05_Hiring_Manager_Toolkit.py", "Hiring Manager Toolkit", "Playbook, onboarding steps, expectations."),
        ("06_Interview_Feedback_Collector.py", "Interview Feedback Collector", "Capture interview outcomes to a log.")
    ]

    for page_file, title, desc in tiles:
        st.markdown(
            f'''
            <a class="tile" href="/?page={page_file}">
              <div>
                <div class="kicker">Tool</div>
                <h3>{title}</h3>
                <p>{desc}</p>
              </div>
              <div>➡️</div>
            </a>
            ''',
            unsafe_allow_html=True
        )

    # 1 long bottom tile
    st.markdown(
        f'''
        <a class="tile long" href="/?page=07_Shortlisting_Summary_Tool.py">
            <div>
              <div class="kicker">Tool</div>
              <h3>Shortlisting Summary Tool</h3>
              <p>Upload up to five CVs + a JD to generate an executive comparison.</p>
            </div>
            <div>➡️</div>
        </a>
        ''',
        unsafe_allow_html=True
    )

    st.markdown('</div>', unsafe_allow_html=True)

# Lightweight router so tiles can deep-link using query param
page = st.query_params.get("page", None)
if page:
    # Streamlit multi-page uses /pages; simulate redirect
    st.switch_page(f"pages/{page}")
