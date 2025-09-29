import streamlit as st
from pathlib import Path
import base64
from urllib.parse import quote

def _find_logo_file():
    # Prefer raster formats first (PNG/JPG/etc.), then SVG
    names = ["neogen_logo", "logo"]
    raster_exts = [".png", ".jpg", ".jpeg", ".webp", ".gif"]
    svg_exts = [".svg"]
    for n in names:
        for ext in raster_exts:
            p = Path("assets") / f"{n}{ext}"
            if p.exists():
                return p
    for n in names:
        for ext in svg_exts:
            p = Path("assets") / f"{n}{ext}"
            if p.exists():
                return p
    return None

def _data_uri(path: Path) -> str | None:
    ext = path.suffix.lower()
    if ext == ".svg":
        txt = path.read_text(encoding="utf-8")
        return "data:image/svg+xml;utf8," + quote(txt)
    mime = {
        ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".gif": "image/gif", ".webp": "image/webp"
    }.get(ext)
    if not mime:
        return None
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"

def header(title: str, kicker: str = "Neogen HR Suite"):
    path = _find_logo_file()
    if path:
        uri = _data_uri(path)
        logo_html = f'<img src="{uri}" alt="Neogen" style="height:34px;display:block;" />' if uri else ""
    else:
        # Blue square fallback so it's obvious if a logo wasn't found
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
