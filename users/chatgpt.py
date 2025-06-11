# users/chatgpt.py

import requests
import json
from django.conf import settings

CHATGPT_API_KEY = settings.CHATGPT_API_KEY
CHATGPT_MODEL = settings.CHATGPT_MODEL

def call_chatgpt(prompt):
    if not CHATGPT_API_KEY:
        raise ValueError("CHATGPT_API_KEY not found")

    instructions = (
        "Reply concisely in one short paragraph and, if applicable, list at most 5 bullet points."
    )

    messages = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": prompt}
    ]

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {CHATGPT_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": CHATGPT_MODEL,
        "messages": messages,
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        try:
            return response.json()["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError):
            return "Sorry, I didn't get that."
    else:
        print(f"Error {response.status_code}: {response.text}")
        return "Something went wrong with ChatGPT."
