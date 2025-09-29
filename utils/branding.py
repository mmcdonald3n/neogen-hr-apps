import streamlit as st
from pathlib import Path
from urllib.parse import quote
import base64, mimetypes

def _find_logo_file() -> Path | None:
    repo_root = Path(__file__).resolve().parents[1]
    search_dirs = [Path.cwd(), repo_root]
    names = ["neogen_logo", "logo"]
    exts  = [".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"]
    for d in search_dirs:
        for n in names:
            for ext in exts:
                p = d / "assets" / f"{n}{ext}"
                if p.exists():
                    return p
    return None

def _logo_data_uri(p: Path) -> str:
    if p.suffix.lower() == ".svg":
        data = p.read_text(encoding="utf-8")
        return "data:image/svg+xml;utf8," + quote(data)
    mime, _ = mimetypes.guess_type(p.name)
    if not mime:
        mime = "image/png"
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"

def _read_version() -> str:
    try:
        return Path("VERSION.txt").read_text(encoding="utf-8").strip()
    except Exception:
        return ""

def header(title: str, kicker: str = "Neogen HR Suite", logo_height: int = 44):
    logo_path = _find_logo_file()
    if logo_path:
        logo_html = f'<img src="{_logo_data_uri(logo_path)}" alt="Neogen" style="height:{logo_height}px;width:auto;display:block;" />'
    else:
        logo_html = '<div style="width:140px;height:40px;background:#0072CE;border-radius:8px"></div>'

    # Title row with logo on the RIGHT
    st.markdown(
        f"""
        <style>
        .neogen-header-row {{ display:flex; align-items:center; justify-content:space-between; gap:16px; }}
        .neogen-header-row h1 {{ margin:0; line-height:1.2; }}
        @media (max-width: 720px) {{
          .neogen-header-row {{ flex-direction:column; align-items:flex-start; gap:8px; }}
          .neogen-header-row img {{ height:32px; }}
        }}
        </style>
        <div class="neogen-header-row">
          <h1>{title}</h1>
          {logo_html}
        </div>
        <div style="display:flex;align-items:center;gap:8px;margin:6px 0 0;">
          <div class="neogen-badge">{kicker}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption("Consistent, fast, and high-quality HR workflows.")
    ver = _read_version()
    if ver:
        st.caption(ver)
    # (Temporary) keep this until you confirm the placement; we can remove later.
    st.caption(f"Logo: {'found '+str(logo_path) if logo_path else 'not found in assets/'}")

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
        css = (Path(__file__).resolve().parents[1] / "assets" / "styles.css").read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except Exception:
        pass
