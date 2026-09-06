import os
import json
from google import genai
import streamlit as st

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY missing in Streamlit Secrets")

client = genai.Client(api_key=GEMINI_API_KEY)

def analyze_complaint(title, description, location):

    prompt = f"""
You are an AI campus maintenance complaint classifier.

Analyze the following campus complaint.

Title:
{title}

Description:
{description}

Location:
{location}

Choose the appropriate:

Category:
Electrical
IT
Plumbing
Furniture
Cleaning
Civil
Security
Other

Priority:
Low
Medium
High
Critical

Department:
Electrical Department
IT Department
Plumbing Department
Maintenance Department
Housekeeping
Civil Department
Security Department
General Administration

Return ONLY valid JSON:

{{
    "category": "...",
    "priority": "...",
    "department": "...",
    "reason": "..."
}}
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    text = response.text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    return json.loads(text)