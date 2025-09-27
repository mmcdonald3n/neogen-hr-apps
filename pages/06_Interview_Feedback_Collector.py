import streamlit as st
from utils.branding import header, inject_css
from utils.persistence import init_db, insert_feedback, fetch_all
from pathlib import Path
import pandas as pd
import base64

st.set_page_config(page_title="Interview Feedback Collector", page_icon="🗒️", layout="wide")
inject_css()
header("Interview Feedback Collector")

st.info("Stores entries in a local SQLite database at **data/interview_feedback.db**.")

init_db()

with st.form("feedback_form"):
    c1, c2, c3 = st.columns(3)
    with c1:
        req = st.text_input("Requisition #*", "")
    with c2:
        candidate = st.text_input("Candidate Name*", "")
    with c3:
        interviewer = st.text_input("Your Name*", "")

    rating = st.slider("Overall Rating (1-5)", 1, 5, 3)
    comments = st.text_area("Comments / Evidence")

    files = st.file_uploader("Attach notes/materials (optional)", accept_multiple_files=True)
    submitted = st.form_submit_button("Submit Feedback")

if submitted:
    attach_names = []
    if files:
        Path("data").mkdir(parents=True, exist_ok=True)
        for f in files:
            path = Path("data")/f.name
            with open(path, "wb") as out:
                out.write(f.read())
            attach_names.append(str(path))
    row_id = insert_feedback(req, candidate, interviewer, rating, comments, "; ".join(attach_names))
    st.success(f"Saved entry #{row_id}")

st.markdown("### Feedback Log")
rows = fetch_all()
if rows:
    df = pd.DataFrame(rows, columns=["id","requisition","candidate","interviewer","rating","comments","attachments","created_at"])
    st.dataframe(df, use_container_width=True)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Export CSV", data=csv, file_name="interview_feedback.csv", mime="text/csv")
else:
    st.write("No records yet.")
