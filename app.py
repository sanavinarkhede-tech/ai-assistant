
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="🎓",
    layout="centered"
)

PERSONALITIES = {
    "Friendly": """
You are a friendly, enthusiastic, and encouraging Study Assistant.
Explain difficult concepts in simple, beginner-friendly language.
Use analogies and real-world examples.
Ask a follow-up question to check the student's understanding.
""",
    "Academic": """
You are a professional university professor and Study Assistant.
Explain concepts accurately using precise terminology and clear structure.
Use relevant examples and balance detail with clarity.
Ask a follow-up question to check the student's understanding.
"""
}

st.title("🎓 AI Study Assistant")
st.caption("Learn smarter with your personal AI tutor.")

# Load API key securely from Streamlit Secrets
api_key = st.secrets.get("Gemini_Api_Key", "")

if not api_key:
    st.error(
        "Gemini API key is missing. Add it under "
        "your Streamlit Cloud app's Settings → Secrets."
    )
    st.stop()

client = genai.Client(api_key=api_key)

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Settings")

    persona = st.selectbox(
        "Choose your learning personality",
        ["Friendly", "Academic"]
    )

    st.markdown("---")
    st.write("Ask questions about:")
    st.write("- Python and programming")
    st.write("- Mathematics and DSA")
    st.write("- AI, ML and Generative AI")
    st.write("- Electrical Engineering")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
question = st.chat_input("Ask your study question...")

if question:
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Your AI tutor is thinking..."):
            try:
                # Send recent conversation for context
                history = st.session_state.messages[-12:]

                conversation = [
                    {
                        "role": (
                            "user" if item["role"] == "user"
                            else "model"
                        ),
                        "parts": [{"text": item["content"]}]
                    }
                    for item in history
                ]

                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=conversation,
                    config=types.GenerateContentConfig(
                        system_instruction=PERSONALITIES[persona],
                        temperature=0.4,
                        max_output_tokens=2000,
                    ),
                )

                answer = response.text

                if not answer:
                    answer = "I couldn't generate a response. Please try again."

                st.markdown(answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

            except Exception:
                st.error(
                    "I couldn't generate an answer. Check that your "
                    "Gemini API key is valid, the model ID is available "
                    "to your account, and your API quota is not exhausted."
                )
