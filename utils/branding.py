import streamlit as st
from pathlib import Path
import base64
from urllib.parse import quote

def _find_logo_file() -> Path | None:
    # Prefer raster formats first, then SVG
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

def _svg_data_uri(p: Path) -> str:
    return "data:image/svg+xml;utf8," + quote(p.read_text(encoding="utf-8"))

def header(title: str, kicker: str = "Neogen HR Suite", logo_width: int = 140):
    # Top row: logo + kicker (side by side), then title + caption
    c1, c2 = st.columns([1, 9], gap="small")
    logo_path = _find_logo_file()

    with c1:
        if logo_path:
            if logo_path.suffix.lower() == ".svg":
                # Inline the SVG via HTML to control size
                uri = _svg_data_uri(logo_path)
                st.markdown(f'<img src="{uri}" alt="Neogen" style="width:{logo_width}px; display:block;" />',
                            unsafe_allow_html=True)
            else:
                # PNG/JPG/WebP/GIF: st.image is most reliable
                st.image(str(logo_path), width=logo_width)
        else:
            # Obvious fallback so you know if logo wasn't found
            st.markdown('<div style="width:140px;height:40px;background:#0072CE;border-radius:8px"></div>',
                        unsafe_allow_html=True)

    with c2:
        st.markdown(f'<div class="neogen-badge">{kicker}</div>', unsafe_allow_html=True)

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
