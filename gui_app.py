import streamlit as st
from agent.chat_agent import run_agent

st.set_page_config(
    page_title="Gemini AI",
    page_icon="🤖"
)

st.title("🤖 Gemini Financial Advisor")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

prompt = st.chat_input("Type a message...")

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    try:
        response = run_agent(prompt)

    except Exception as e:
        response = f"ERROR: {e}"

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": str(response)
        }
    )

    st.rerun()