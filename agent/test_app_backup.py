import pandas as pd
import re
import streamlit as st
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

st.title("💰 AI Financial Advisor")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.write(message["content"])

prompt = st.chat_input("Ask me anything about money...")

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        # Extract reply text (SDK may vary; fall back to string conversion)
        ai_reply = getattr(response, "text", None) or str(response)
    except Exception:
        ai_reply = (
            "⚠️ Gemini is currently busy.\n\n"
            "Please try again in a few seconds."
        )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": ai_reply
        }
    )

    st.rerun()