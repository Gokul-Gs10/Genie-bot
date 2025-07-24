# backend/chatbot.py

import os
from datetime import datetime
from backend.firebase import init_firebase
import requests

# --- API Configurations ---
PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY")
PERPLEXITY_MODEL = "sonar-pro"
PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"

# --- Load last N messages from Firestore ---
def get_chat_history(company_name, limit=10):
    db = init_firebase()
    chats_ref = db.collection("companies").document(company_name).collection("chats")
    chats = chats_ref.order_by("timestamp", direction="ASCENDING").limit(limit).stream()

    messages = [
        {
            "role": "system",
            "content": (
                "You are StartGenieBot, an expert assistant helping startup founders with ideation, "
                "product planning, marketing, and execution strategy. "
                "Whenever the user's request has several aspects, steps, or options, respond using "
                "clear bullet points or numbered lists in markdown, so your answers are easy to scan."
            )
        }
    ]

    for chat in chats:
        c = chat.to_dict()
        messages.append({"role": "user", "content": c["prompt"]})
        messages.append({"role": "assistant", "content": c["response"]})

    return messages

# --- Confirmatory Phrases Checker ---
def check_confirmation(user_input: str) -> bool:
    confirmations = [
        "yes i confirm", "i confirm", "yes we can confirm", "we can proceed",
        "yes proceed", "save it", "confirm", "yes, save", "finalize it", "okay, confirmed"
    ]
    user_input = user_input.lower().strip()
    return any(conf in user_input for conf in confirmations)

# --- Main Chat Handler ---
def ask_ai(prompt: str, company_name: str) -> str:
    try:
        if not PERPLEXITY_API_KEY:
            return "[ERROR] API key not provided. Set PERPLEXITY_API_KEY environment variable."

        messages = get_chat_history(company_name)
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": PERPLEXITY_MODEL,
            "messages": messages,
            "max_tokens": 500
        }

        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(PERPLEXITY_URL, headers=headers, json=payload)
        response.raise_for_status()
        reply = response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()

        # Save chat history
        store_chat(company_name, prompt, reply)

        # Save finalized plans marked explicitly by model
        if "[FINALIZED]" in reply:
            store_finalized_idea(company_name, prompt, reply)
            create_company_folder(company_name)

        # Save confirmed requirements from user
        if check_confirmation(prompt) and len(messages) >= 2:
            last_prompt = messages[-2]["content"]
            last_response = messages[-1]["content"]
            store_confirmed_requirement(company_name, last_prompt, last_response)

        return reply

    except Exception as e:
        return f"[ERROR] {str(e)}"

# --- Firestore: Store raw chat ---
def store_chat(company_name: str, prompt: str, response: str):
    db = init_firebase()
    db.collection("companies").document(company_name).collection("chats").add({
        "prompt": prompt,
        "response": response,
        "timestamp": datetime.utcnow()
    })

# --- Firestore: Store finalized idea (from model) ---
def store_finalized_idea(company_name: str, prompt: str, response: str):
    db = init_firebase()
    db.collection("companies").document(company_name).set({
        "finalized_idea": response,
        "original_prompt": prompt,
        "last_updated": datetime.utcnow()
    }, merge=True)

# --- Firestore: Confirmed user message and response ---
def store_confirmed_requirement(company_name: str, prompt: str, response: str):
    db = init_firebase()
    db.collection("companies").document(company_name).collection("confirmed_requirements").add({
        "user_prompt": prompt,
        "bot_response": response,
        "confirmed_at": datetime.utcnow()
    })

# --- Create local company folder (optional) ---
def create_company_folder(company_name):
    folder_path = f"backend/companies/{company_name}"
    os.makedirs(folder_path, exist_ok=True)

# --- Optional: Store company + user metadata (one-time onboarding) ---
def store_company_metadata(company_name: str, person: str, designation: str):
    db = init_firebase()
    db.collection("companies").document(company_name).set({
        "metadata": {
            "company_name": company_name,
            "contact_person": person,
            "designation": designation,
            "status": "draft",
            "created_at": datetime.utcnow(),
            "last_updated": datetime.utcnow()
        }
    }, merge=True)