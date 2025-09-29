import streamlit as st
from pathlib import Path
import base64
from urllib.parse import quote

def _logo_data_uri():
    """
    Return a data: URI for the first logo found in assets.
    Supports: .svg, .png, .jpg, .jpeg, .gif, .webp
    """
    candidates = [
        "assets/neogen_logo.svg", "assets/neogen_logo.png", "assets/neogen_logo.jpg", "assets/neogen_logo.jpeg",
        "assets/logo.svg",        "assets/logo.png",        "assets/logo.jpg",        "assets/logo.jpeg",
        "assets/neogen_logo.webp","assets/logo.webp","assets/neogen_logo.gif","assets/logo.gif"
    ]
    for c in candidates:
        p = Path(c)
        if p.exists():
            ext = p.suffix.lower()
            if ext == ".svg":
                txt = p.read_text(encoding="utf-8")
                # URL-encode the SVG so it’s safe inside the src attribute
                return "data:image/svg+xml;utf8," + quote(txt)
            else:
                mime = {
                    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                    ".gif": "image/gif", ".webp": "image/webp"
                }.get(ext, "application/octet-stream")
                b64 = base64.b64encode(p.read_bytes()).decode("ascii")
                return f"data:{mime};base64,{b64}"
    return None

def header(title: str, kicker: str = "Neogen HR Suite"):
    logo = _logo_data_uri()
    # Fallback block if no logo found
    if logo:
        logo_html = f'<img src="{logo}" alt="Neogen"/>'
    else:
        logo_html = '<div style="width:34px;height:34px;background:#0072CE;border-radius:8px"></div>'

    st.markdown(
        f"""
        <div class="neogen-header">
            {logo_html}
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
