# -*- coding: utf-8 -*-
import streamlit as st
from utils.branding import header, sidebar_model_controls, inject_css
from utils.llm import chat_complete
from utils.parsers import extract_text_from_upload
from utils.exporters import interview_pack_to_docx_bytes  # boxed DOCX

st.set_page_config(page_title="Interview Guide Generator", page_icon="🧩")
header("Interview Guide Generator")
st.success("Page header loaded cleanly. Now restore the full body below this header.")
