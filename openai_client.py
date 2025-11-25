# openai_client.py

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # loads .env

# Initialize client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# SYSTEM PROMPT
PROMPT_SYSTEM = """
You are AS Smart Suite Assistant, a professional business assistant.
You help customers with software recommendations, ask questions,
and collect leads if the user is interested in purchase.
"""

def ask_assistant(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=300,
            temperature=0.4
        )

        return response.choices[0].message.content

    except Exception as e:
        print("OpenAI error:", e)
        return "Sorry, I'm having trouble reaching the AI engine right now. Please try again later."
