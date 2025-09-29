import streamlit as st
from utils.branding import header, sidebar_model_controls, inject_css
from utils.llm import chat_complete
from pathlib import Path
import pandas as pd

st.set_page_config(page_title="Job Description Generator", page_icon="📝", layout="wide")
inject_css()
header("Job Description Generator")

model, temp, max_tokens = sidebar_model_controls()

HOUSE_STYLE_PATH = Path("house_style/NEOGEN_HOUSE_STYLE_JD.md")
house_style_text = HOUSE_STYLE_PATH.read_text(encoding="utf-8") if HOUSE_STYLE_PATH.exists() else "# Neogen JD House Style (missing)\\n"
st.info("House Style is centrally controlled. JDs are always generated to Neogen House Style.")

# Levels S1–S5 and M1–M6 only
levels_df = pd.read_csv("house_style/JOB_LEVELS.csv")
levels_df = levels_df[levels_df["Code"].str.startswith(("S","M"))].copy()
levels_df["Display"] = levels_df.apply(lambda r: f"{r['Code']} – {r['Name']} ({r['Descriptor']})", axis=1)
order = list(levels_df[levels_df["Code"].str.startswith("S")]["Code"].unique()) + \
        list(levels_df[levels_df["Code"].str.startswith("M")]["Code"].unique())
display_order = [levels_df.loc[levels_df["Code"]==c, "Display"].item() for c in order]

# Countries from Neogen list
countries = pd.read_csv("house_style/NEOGEN_COUNTRIES.csv")["Country"].dropna().tolist() \
    if Path("house_style/NEOGEN_COUNTRIES.csv").exists() else ["United Kingdom","United States"]

def default_detail_for(level_code: str) -> int:
    return 7 if level_code.startswith("M") else 5

def tone_label(v:int) -> str:
    return ("Plain / Direct","Professional / Neutral","Polished / Executive","Formal / High-polish")[(0,2,4,7,10).index(max([x for x in (0,2,4,7,10) if v>=x]))]

def detail_label(v:int) -> str:
    if v <= 3: return "Concise (lean)"
    if v <= 6: return "Standard (balanced)"
    if v <= 8: return "Detailed (thorough)"
    return "Very Detailed (comprehensive)"

with st.form("jd_form"):
    c1, c2, c3 = st.columns([2,2,2])
    with c1:
        job_title = st.text_input("Job Title*", placeholder="e.g., Senior QA Analyst")
    with c2:
        level_choice_display = st.selectbox("Level*", display_order)
        level_code = order[display_order.index(level_choice_display)]
    with c3:
        country = st.selectbox("Country*", countries, index=min(0, len(countries)-1))

    c4, c5 = st.columns([2,2])
    with c4:
        tone = st.slider("Tone", 0, 10, 5, help="Plain → Formal")
    with c5:
        detail_default = default_detail_for(level_code)
        detail = st.slider("Level of Detail", 0, 10, detail_default, help="Concise → Very Detailed")

    notes = st.text_area("Optional: Add key data (team, systems, travel, compliance, reporting line, etc.)",
                         height=120, placeholder="Leave blank if not needed.")

    submitted = st.form_submit_button("Generate JD")

if submitted:
    if not job_title:
        st.error("Please provide a Job Title.")
        st.stop()
    if level_code.startswith("M") and detail < 6:
        detail = 6

    system = "You are an HR content generator. Output must follow the Neogen House Style. Use inclusive, bias-aware language."
    user_prompt = f"""
HOUSE_STYLE (read-only):
{house_style_text}

CONTEXT:
- Job Title: {job_title}
- Level: {level_code}
- Country: {country}
- Tone: {tone_label(tone)} (slider={tone})
- Detail: {detail_label(detail)} (slider={detail})
- Optional Notes (may be empty):
{notes}

REQUIREMENTS:
- Produce a complete Job Description in the Neogen House Style above.
- Automatically adjust scope and sophistication based on level:
  * S1–S2: narrow responsibilities; no management duties.
  * S3–S5: specialist impact; growing autonomy.
  * M1–M3: team leadership, planning, stakeholder coordination.
  * M4–M6: strategic scope, cross-functional leadership, measurable outcomes.
- Tailor spelling/phrasing to the country (e.g., UK vs US English). Do not give legal advice.
- Clear headings, bullet lists, and concise, inclusive language.

OUTPUT FORMAT:
Markdown only. Start with the Job Title as H1, then sections per House Style (Role Purpose, Key Responsibilities, Required/Preferred Qualifications, Competencies, Work Pattern, etc.).
"""
    with st.spinner("Generating JD..."):
        out = chat_complete(
            model,
            [{"role":"system","content":system},{"role":"user","content":user_prompt}],
            temperature=temp,
            max_tokens=max_tokens
        )
    st.markdown("### Output")
    st.download_button(
        "Download as .md",
        data=out.encode("utf-8"),
        file_name=f"{job_title.replace(' ','_')}_JD.md",
        mime="text/markdown"
    )
    st.markdown(out)
