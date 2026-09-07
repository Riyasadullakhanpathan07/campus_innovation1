
import streamlit as st
from google import genai

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY missing in Streamlit Secrets")

client = genai.Client(api_key=GEMINI_API_KEY)


def analyze_complaint(title, description, location):

    response = client.models.generate_content(
        model="gemini-3.7-flash",
        contents="Reply with exactly: OK"
    )

    return {
        "category": "Other",
        "priority": "Medium",
        "department": "General Administration",
        "reason": response.text
    }
