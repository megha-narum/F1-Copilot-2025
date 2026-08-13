"""
app.py — Web interface for the F1 Copilot.

This is a thin visual layer on top of the same router/agents logic
used by main.py — no product logic is duplicated here. Styling comes
entirely from .streamlit/config.toml (F1 red accent, light background),
not custom CSS, to keep this simple and easy to maintain.

Usage:
    streamlit run app.py
"""

import streamlit as st
from router import route
from agents import strategy_agent, general_agent

AGENTS = {
    "strategy": strategy_agent,
    "general": general_agent,
}

st.set_page_config(page_title="F1 2025 Copilot", page_icon="🏁", layout="centered")

# --- Header ---
# If you have rights to a real F1 logo image file, drop it in this
# folder and uncomment the line below to display it instead of the
# text wordmark.
# st.image("f1_logo.png", width=120)

st.title("🏁 F1 2025 Copilot")
st.caption("Ask about the 2025 season — every answer is grounded in a real, cited source.")

st.divider()

# --- Session state: keep a running chat history ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Empty state: example questions ---
if not st.session_state.messages:
    st.markdown("**Try asking:**")
    st.markdown("- Who won the Bahrain Grand Prix?")
    st.markdown("- What does a blue flag mean?")
    st.markdown("- Why do F1 cars throw sparks?")
    st.markdown("")

# --- Render chat history ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --- Chat input ---
question = st.chat_input("Ask about the 2025 F1 season...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Looking that up..."):
            category = route(question)

            if category == "unclear":
                answer = "I can only help with F1-related questions."
            elif category == "needs_live_data":
                answer = (
                    "Sorry! I can't answer questions about live or ongoing "
                    "F1 info — but go ahead and ask me about a specific "
                    "2025 Grand Prix!"
                )
            else:
                answer = AGENTS[category](question)

            st.write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
