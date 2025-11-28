from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import os
import requests

from openai_client import ask_assistant, PROMPT_SYSTEM


app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# serve static files
#app.mount("/static", StaticFiles(directory="static"), name="static")


class ChatRequest(BaseModel):
    user_message: str


ZAPIER_WEBHOOK_URL = os.getenv("ZAPIER_WEBHOOK_URL")


def send_lead_to_zapier(lead_data):
    if not ZAPIER_WEBHOOK_URL:
        print("Zapier webhook URL not found")
        return {"status": "error", "message": "Zapier URL missing"}

    try:
        response = requests.post(ZAPIIER_WEBHOOK_URL, json=lead_data)
        response.raise_for_status()
        return {"status": "success", "message": "Lead sent to Zapier"}
    except Exception as e:
        print(f"Error sending lead to Zapier: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/chat")
async def chat(payload: ChatRequest):
    messages = [
        {"role": "system", "content": PROMPT_SYSTEM},
        {"role": "user", "content": payload.user_message}
    ]

    ai_response = ask_assistant(messages)

    # try to detect JSON lead
    try:
        if isinstance(ai_response, str) and ai_response.strip().startswith("{"):
            data = json.loads(ai_response)

            if "lead" in data and data.get("status") == "confirmed":
                lead = data["lead"]

                # save locally
                with open("leads.json", "a") as f:
                    f.write(json.dumps(lead) + "\n")

                # send to zapier
                send_lead_to_zapier(lead)

    except Exception as e:
        print("Lead parsing error:", e)

    return {"reply": ai_response}


from dotenv import load_dotenv
load_dotenv()

@app.post("/lead_webhook")
async def lead_webhook(request: Request):
    payload = await request.json()

    # store locally
    try:
        os.makedirs("data", exist_ok=True)
        with open("data/leads.json", "a") as f:
            f.write(json.dumps(payload) + "\n")
    except Exception as e:
        print("Error saving lead:", e)
        return {"status": "error", "error": str(e)}

    # forward to external zapier webhook
    if ZAPIER_WEBHOOK_URL:
        try:
            requests.post(ZAPIER_WEBHOOK_URL, json=payload)
        except Exception as e:
            print("Error forwarding lead:", e)

    return {"status": "ok", "received": payload}

