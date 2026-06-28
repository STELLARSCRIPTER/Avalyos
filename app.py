"""
AVALYOS Streamlit Frontend Application - Clean, minimal version.
"""

import streamlit as st
import requests
from utils import load_data, call_backend_health, get_all_companies

st.set_page_config(page_title="AVALYOS Quantum Intelligence", page_icon="🌍", layout="wide", initial_sidebar_state="collapsed")

light_theme_css = """<style>
:root { --primary: #0066ff; --bg: #ffffff; --card: #f0f2f6; --text: #262730; --muted: #666666; --border: #e6e9ee; --success: #00a86b; --error: #d32f2f; }
body, .stApp { background-color: var(--bg) !important; color: var(--text) !important; }
.hero-section { background-color: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 2.5rem; margin-bottom: 1.5rem; }
.feature-card { background-color: transparent; border: 1px solid var(--border); border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem; }
.status-badge { display: inline-block; padding: 0.4rem 0.8rem; background-color: var(--card); border: 1px solid var(--border); border-radius: 6px; font-size: 0.85rem; font-weight: 600; color: var(--text); }
.status-online { color: var(--success); }
.status-offline { color: var(--error); }
.stButton>button { white-space: nowrap; }
</style>"""

st.markdown(light_theme_css, unsafe_allow_html=True)

try:
    data = load_data("companies.json")
except FileNotFoundError:
    st.error("Error: companies.json not found.")
    st.stop()

st.sidebar.markdown("### AVALYOS")
st.sidebar.markdown("**Quantum Intelligence Platform**")
st.sidebar.markdown("---")

if "_sidebar_health_container" not in st.session_state:
    st.session_state["_sidebar_health_container"] = st.sidebar.container()

with st.session_state["_sidebar_health_container"]:
    backend_status = call_backend_health()
    col_a, col_b = st.columns([3, 1])
    with col_a:
        st.markdown(f'<span class="status-badge status-{("online" if backend_status else "offline")}">{"🟢 Online" if backend_status else "🔴 Offline"}</span>', unsafe_allow_html=True)
    with col_b:
        if st.button("Refresh", key="refresh_status"):
            st.rerun()
    if not backend_status:
        st.warning("Backend offline. Start: uvicorn aval_backend:app --host 0.0.0.0 --port 8000")

st.sidebar.markdown("---\n**Navigate To:**\n- Global Company Navigator\n- Quantum Simulator\n- Company Browser")

st.markdown('<div class="hero-section"><h1 style="color: var(--primary);">QUANTUM INTELLIGENCE</h1><p style="color: var(--muted);">Navigate global companies with quantum analytics.</p></div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
try:
    company_count = len(data.get("companies", {}))
    branch_count = len(get_all_companies(data))
    with col1: st.metric("Status", "Online" if backend_status else "Offline")
    with col2: st.metric("Companies", company_count)
    with col3: st.metric("Continents", len(data.get("continents", {})))
    with col4: st.metric("Branches", branch_count)
except Exception:
    pass

st.markdown("---")
st.subheader("Platform Features")

features = [
    ("Global Navigator", "Explore companies by hierarchy"),
    ("Quantum Sampling", "Advanced quantum algorithms"),
    ("Real-Time Analysis", "Monte Carlo simulations"),
    ("Company Intelligence", "Search and analyze"),
]

col1, col2 = st.columns(2)
for i, (title, desc) in enumerate(features):
    with col1 if i % 2 == 0 else col2:
        st.write(f"**{title}**\n{desc}")

st.markdown("---\nAVALYOS Quantum Intelligence Platform | Built with Streamlit • FastAPI • Quantum Enabled")

# Meridian modal popup (accessible from the sidebar)
PRESET_QUESTIONS = [
    "What is Avalyos and how does it work within DIOS?",
    "How are industries and companies structured in Avalyos?",
    "What kind of analysis and simulations does Avalyos provide?",
    "How should I interpret the outputs and scores shown in the platform?",
    "What features will be enabled once datasets are integrated?",
]

if "meridian_messages" not in st.session_state:
    st.session_state.meridian_messages = []


def _send_to_backend(text: str) -> str:
    try:
        resp = requests.post("http://localhost:8000/chat", json={"message": text}, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("reply", "(no reply)")
        return f"Backend error {resp.status_code}: {resp.text}"
    except Exception as e:
        return f"Failed to contact backend: {e}"


@st.dialog("Meridian — Product Guide")
def meridian_dialog():
    st.header("Meridian — Guided Product Assistant")
    st.write(
        "Meridian explains AVALYOS features and helps you find functionality. "
        "Ask one of the preset questions or type your own. Meridian focuses on product "
        "guidance, not general-purpose generation."
    )

    cols = st.columns(5)
    for i, q in enumerate(PRESET_QUESTIONS):
        with cols[i % 5]:
            if st.button(q, key=f"preset_{i}"):
                st.session_state.meridian_messages.append({"role": "user", "text": q})
                reply = _send_to_backend(q)
                st.session_state.meridian_messages.append({"role": "meridian", "text": reply})

    with st.form("meridian_form"):
        user_text = st.text_area("Ask Meridian", height=120, key="meridian_input")
        submitted = st.form_submit_button("Send")
        if submitted and user_text.strip():
            st.session_state.meridian_messages.append({"role": "user", "text": user_text})
            reply = _send_to_backend(user_text)
            st.session_state.meridian_messages.append({"role": "meridian", "text": reply})

    st.markdown("---")
    for m in st.session_state.meridian_messages:
        if m["role"] == "user":
            st.markdown(f"**You:** {m['text']}")
        else:
            st.markdown(f"**Meridian:** {m['text']}")


if st.sidebar.button("Meridian — Help", key="open_meridian"):
    meridian_dialog()



