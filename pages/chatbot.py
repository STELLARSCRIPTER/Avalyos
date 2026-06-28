import streamlit as st
import requests

st.set_page_config(page_title="Meridian — Product Guide", page_icon="🧭")
st.title("Meridian — Product Guide")
st.write("Meridian is a guided assistant that explains AVALYOS features and helps you find functionality — not a general-purpose generative AI.")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_area("Your question for Meridian", height=120)
    submitted = st.form_submit_button("Ask Meridian")

if submitted and user_input:
    st.session_state.messages.append({"role": "user", "text": user_input})
    try:
        resp = requests.post("http://localhost:8000/chat", json={"message": user_input}, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            reply = data.get("reply") or "(no reply)"
        else:
            reply = f"Error from backend: {resp.status_code} {resp.text}"
    except Exception as e:
        reply = f"Failed to contact backend: {e}"
    st.session_state.messages.append({"role": "meridian", "text": reply})

for m in st.session_state.messages:
    if m["role"] == "user":
        st.markdown(f"**You:** {m['text']}")
    else:
        st.markdown(f"**Meridian:** {m['text']}")

st.markdown("---")
st.markdown("Tips: ask about features, navigation, or how to run simulations.")
