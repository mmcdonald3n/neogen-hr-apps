# -*- coding: utf-8 -*-
import streamlit as st
from utils.branding import header, inject_css

st.set_page_config(page_title="Interview Guide Generator", page_icon="🧩")
header("Interview Guide Generator")
inject_css()
st.success("Header loaded cleanly. If you see this, the indentation issue is gone.")