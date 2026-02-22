"""Streamlit UI for SREC Cypher Bot."""

from pathlib import Path
from typing import Optional

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_LOGO_CANDIDATES = [
    BASE_DIR / "assets" / "logo.png",
    BASE_DIR / "assets" / "logo.jpg",
    BASE_DIR / "assets" / "logo.jpeg",
]


st.set_page_config(page_title="SREC Cypher Bot", page_icon="🛡️", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at 20% 0%, #25103a 0%, #0a0f1f 40%, #060b18 100%);
        color: #f2f5ff;
    }
    .app-shell {
        max-width: 1100px;
        margin: 1rem auto;
        padding: 1.25rem 1.25rem 2rem 1.25rem;
    }
    .hero {
        display: flex;
        align-items: center;
        gap: 1.25rem;
        margin-bottom: 1rem;
    }
    .hero-title {
        font-size: 3rem;
        line-height: 1.05;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(90deg, #62d2ff 0%, #b56dff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        margin-top: 0.25rem;
        color: #b9c6e8;
        font-size: 1.25rem;
    }
    .status-pill {
        display: inline-block;
        margin-top: 0.5rem;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        font-size: 0.86rem;
        font-weight: 600;
    }
    .connected { background: #133f2a; color: #8ff5b4; border: 1px solid #2a6b4f; }
    .disconnected { background: #402132; color: #ffb4d8; border: 1px solid #7e3d64; }
    .prompt-label {
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        font-size: 1.25rem;
        font-weight: 600;
    }
    .response-card {
        background: linear-gradient(180deg, #141c31 0%, #11162a 100%);
        border: 1px solid #2c3452;
        border-radius: 14px;
        padding: 1rem;
        margin-top: 1rem;
        color: #e8eeff;
        min-height: 72px;
    }
    .debug-card {
        background: #0f162a;
        border: 1px solid #2a3557;
        border-left: 4px solid #2fb5ff;
        border-radius: 10px;
        padding: 0.75rem 1rem;
        margin-top: 0.75rem;
        color: #b8caf1;
        font-size: 0.95rem;
    }
    .footer {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #2a3557;
        color: #8d9cc2;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_default_logo_path() -> Optional[Path]:
    for candidate in DEFAULT_LOGO_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def init_engine() -> None:
    if "engine_checked" in st.session_state:
        return

    st.session_state.engine_checked = True
    st.session_state.engine = None
    st.session_state.engine_error = ""

    try:
        from engine import SRECCypherEngine  # Local import for graceful fallback

        st.session_state.engine = SRECCypherEngine()
    except Exception as exc:  # Keep UI alive and show debug state
        st.session_state.engine_error = f"{type(exc).__name__}: {exc}"


if "messages" not in st.session_state:
    st.session_state.messages = []

init_engine()
engine_connected = st.session_state.engine is not None

st.markdown('<div class="app-shell">', unsafe_allow_html=True)

logo_col, header_col = st.columns([1, 5])
with logo_col:
    uploaded_logo = st.file_uploader("", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    if uploaded_logo:
        st.image(uploaded_logo, width=130)
    else:
        default_logo = get_default_logo_path()
        if default_logo:
            st.image(str(default_logo), width=130)

with header_col:
    st.markdown('<h1 class="hero-title">SREC Cypher Bot</h1>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">Create, explore, and ask secure college queries</div>',
        unsafe_allow_html=True,
    )
    if engine_connected:
        st.markdown('<span class="status-pill connected">AI Engine Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-pill disconnected">AI Engine Not Connected</span>', unsafe_allow_html=True)

st.markdown('<div class="prompt-label">Ask something about the college</div>', unsafe_allow_html=True)
user_query = st.text_input("", placeholder="Type your question…", label_visibility="collapsed")

if user_query:
    if engine_connected:
        result = st.session_state.engine.ask(user_query)
        st.session_state.messages.append({"role": "user", "content": user_query})
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": result["answer"],
                "status": result["status"],
            }
        )
    else:
        st.session_state.messages.append({"role": "user", "content": user_query})
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": "🛠️ Secure response will appear here once AI engine is connected.",
                "status": "ENGINE_DISCONNECTED",
            }
        )

if st.session_state.messages:
    for msg in st.session_state.messages[-6:]:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f'<div class="response-card">{msg["content"]}</div>', unsafe_allow_html=True)
else:
    st.markdown(
        '<div class="response-card">🛠️ Secure response will appear here once AI engine is connected.</div>',
        unsafe_allow_html=True,
    )

if not engine_connected:
    err = st.session_state.engine_error or "Unknown startup issue"
    st.markdown(
        f'<div class="debug-card"><b>Debug:</b> AI engine not connected. Details: <code>{err}</code></div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="footer">🔐 Powered by Secure RAG AI • SREC Cypher Bot</div></div>',
    unsafe_allow_html=True,
)
