import streamlit as st
from pathlib import Path

def header(title: str, kicker: str = "Neogen HR Suite"):
    st.markdown(
        f"""
        <div class="neogen-header">
            <img src="data:image/svg+xml;utf8,{Path("assets/neogen_logo.svg").read_text(encoding="utf-8")}" alt="Neogen"/>
            <div class="neogen-badge">{kicker}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.title(title)
    st.caption("Consistent, fast, and high-quality HR workflows.")

def sidebar_model_controls():
    st.sidebar.markdown("### Model Settings")
    model = st.sidebar.selectbox(
        "OpenAI model",
        ["gpt-4o-mini","gpt-4.1-mini","gpt-4.1","gpt-4o","gpt-3.5-turbo"],
        index=0
    )
    temp = st.sidebar.slider("Creativity (temperature)", 0.0, 1.0, 0.2, 0.05)
    max_tokens = st.sidebar.slider("Max tokens", 256, 5000, 1800, 64)
    st.sidebar.markdown('<div class="sidebar-note">You can change these anytime.</div>', unsafe_allow_html=True)
    st.sidebar.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    return model, temp, max_tokens

def inject_css():
    try:
        css = Path("assets/styles.css").read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except Exception:
        pass
