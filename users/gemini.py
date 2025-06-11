# users/gemini.py

import requests
import json
from django.conf import settings

GEMINI_API_KEY = settings.GEMINI_API_KEY
GEMINI_MODEL = "gemini-2.0-flash"  # Make sure this is valid for your account

def call_gemini(prompt):
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found")

    instructions = (
    "Reply concisely in one short paragraph and, if applicable, list at most 5 bullet points.\n"
    "At the end, include a 'Summary:' line with a one-sentence summary of your response."
)


    full_prompt = f"{instructions}\n\nUser: {prompt}"

    url = f"https://generativelanguage.googleapis.com/v1/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {"parts": [{"text": full_prompt}]}
        ]
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        try:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError):
            return "Sorry, I didn't get that."
    else:
        print(f"Error {response.status_code}: {response.text}")
        return "Something went wrong with the AI."
