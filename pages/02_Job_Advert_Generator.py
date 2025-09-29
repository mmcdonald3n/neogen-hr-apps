import streamlit as st
from pathlib import Path
from utils.branding import header, sidebar_model_controls, inject_css
from utils.llm import chat_complete
from utils.parsers import extract_text_from_upload
from utils.exporters import markdown_to_docx_bytes

st.set_page_config(page_title="Job Advert Generator", page_icon="📣", layout="wide")
inject_css()
header("Job Advert Generator")

model, temp, max_tokens = sidebar_model_controls()

# Central house style (read-only)
HOUSE_STYLE_PATH = Path("house_style/NEOGEN_AD_HOUSE_STYLE.md")
house_style_text = HOUSE_STYLE_PATH.read_text(encoding="utf-8") if HOUSE_STYLE_PATH.exists() else "# Neogen Advert House Style\n"
st.info("House Style is centrally controlled. Upload any JD and we will convert it to a Neogen house-style advert.")

# Inputs
with st.form("ad_form"):
    c1, c2, c3 = st.columns([2,2,2])

    with c1:
        jd_file = st.file_uploader("Upload source JD (.docx, .pdf, .txt, .md)*",
                                   type=["docx","pdf","txt","md"])
    with c2:
        tone = st.slider("Tone", 0, 10, 5, help="Plain → Formal")
    with c3:
        detail = st.slider("Level of Detail", 0, 10, 5, help="Concise → Detailed")

    # Optional title/location (helps the model)
    c4, c5 = st.columns([2,2])
    with c4:
        job_title_hint = st.text_input("Optional: Job title (if you want to override/influence)")
    with c5:
        location_hint = st.text_input("Optional: Location / work model (e.g., Remote, Hybrid – Glasgow, UK)")

    submitted = st.form_submit_button("Generate Advert")

if submitted:
    if not jd_file:
        st.error("Please upload a source JD.")
        st.stop()

    source_text = extract_text_from_upload(jd_file)
    if not source_text.strip():
        st.error("Could not read any text from that file. Try a different format.")
        st.stop()

    def tone_label(v:int) -> str:
        if v <= 2: return "Plain / Direct"
        if v <= 4: return "Professional / Neutral"
        if v <= 7: return "Polished / Executive"
        return "Formal / High-polish"

    def detail_label(v:int) -> str:
        if v <= 3: return "Concise (lean)"
        if v <= 6: return "Standard (balanced)"
        if v <= 8: return "Detailed (thorough)"
        return "Very Detailed (comprehensive)"

    system = "You are an expert HR content writer. Produce job adverts strictly following the provided House Style. Use inclusive language."
    user_prompt = f"""
HOUSE_STYLE (read-only):
{house_style_text}

SOURCE_JD (free-form text from uploaded file):
\"\"\"{source_text[:20000]}\"\"\"  # (truncated for safety)

GUIDANCE:
- Convert the SOURCE_JD into a high-quality Neogen job advert in the House Style.
- If job_title/location hints are provided, reflect them naturally:
  JobTitleHint={job_title_hint or "None"}, LocationHint={location_hint or "None"}
- Adjust voice and length by sliders:
  Tone={tone_label(tone)} (slider={tone}), Detail={detail_label(detail)} (slider={detail})
- Prefer UK/US spelling consistent with the location if inferable.
- Output **Markdown only** using the style's headings and bullet lists.
"""
    with st.spinner("Drafting advert…"):
        ad_md = chat_complete(
            model,
            [{"role": "system", "content": system},
             {"role": "user", "content": user_prompt}],
            temperature=temp,
            max_tokens=max_tokens
        )

    st.markdown("### Output")
    # st.code gives a built-in copy-to-clipboard button in Streamlit
    st.code(ad_md, language="markdown")

    st.download_button(
        "Download as .docx",
        data=markdown_to_docx_bytes(ad_md, filename_title=(job_title_hint or "Job Advert")),
        file_name=f"{(job_title_hint or 'Job_Advert').replace(' ', '_')}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
