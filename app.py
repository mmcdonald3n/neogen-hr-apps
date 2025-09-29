import streamlit as st
from utils.branding import header, inject_css

st.set_page_config(page_title="Neogen HR Apps", page_icon="✅", layout="wide")
inject_css()

header("HR Apps", kicker="Neogen HR Suite")
st.write("Welcome! Choose a tool below.")

tiles = [
    ("01_Job_Description_Generator.py",  "📝", "Job Description Generator",      "Produce Neogen house-style JDs from options."),
    ("02_Job_Advert_Generator.py",       "📢", "Job Advert Generator",           "Convert JD + options into a branded advert."),
    ("03_Interview_Guide_Generator.py",  "📋", "Interview Guide Generator",      "Structured interview guide templates."),
    ("04_Interview_Question_Generator.py","❓","Interview Question Generator",    "Tailored questions + scoring rubrics."),
    ("05_Hiring_Manager_Toolkit.py",     "🧰", "Hiring Manager Toolkit",          "Playbook, onboarding steps, expectations."),
    ("06_Interview_Feedback_Collector.py","🗒️","Interview Feedback Collector",    "Capture interview outcomes to a log.")
]
long_tile = ("07_Shortlisting_Summary_Tool.py", "🧮", "Shortlisting Summary Tool",
             "Upload up to five CVs + a JD to generate an executive comparison.")

# ---- Build one HTML string with ALL tiles so CSS grid works ----
tiles_html = ['<div class="tile-grid">']
for page_file, emoji, title, desc in tiles:
    tiles_html.append(f"""
    <a class="tile" href="/?page={page_file}">
      <div class="emoji">{emoji}</div>
      <div>
        <div class="kicker">Tool</div>
        <h3>{title}</h3>
        <p>{desc}</p>
      </div>
      <div class="chev">➜</div>
    </a>
    """)

lp, lemoji, ltitle, ldesc = long_tile
tiles_html.append(f"""
<a class="tile long" href="/?page={lp}">
  <div class="emoji">{lemoji}</div>
  <div>
    <div class="kicker">Tool</div>
    <h3>{ltitle}</h3>
    <p>{ldesc}</p>
  </div>
  <div class="chev">➜</div>
</a>
""")
tiles_html.append("</div>")

st.markdown("".join(tiles_html), unsafe_allow_html=True)

# Router
page = st.query_params.get("page", None)
if page:
    st.switch_page(f"pages/{page}")
