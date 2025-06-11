# users/groq.py

import requests
from django.conf import settings

GROQ_API_KEY = settings.GROQ_API_KEY
GROQ_MODEL = settings.GROQ_MODEL

def call_groq(prompt):
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not found")

    instructions = (
    "Reply concisely in one short paragraph and, if applicable, list at most 5 bullet points.\n"
    "At the end, include a 'Summary:' line with a one-sentence summary of your response."
)


    messages = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": prompt}
    ]

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
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
        print(f"Groq Error {response.status_code}: {response.text}")
        return "Something went wrong with Groq."
