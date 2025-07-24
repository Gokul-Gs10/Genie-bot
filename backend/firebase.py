# backend/firebase.py
import firebase_admin
from firebase_admin import credentials, firestore
import os

firebase_app = None

def init_firebase():
    global firebase_app
    if not firebase_app:
        cred_path = os.path.join(os.getcwd(), "backend/fire_base_key.json")
        cred = credentials.Certificate(cred_path)
        firebase_app = firebase_admin.initialize_app(cred)
    return firestore.client()

def store_report_data(company_name, date_range, summary):
    db = init_firebase()
    doc_ref = db.collection("reports").document(company_name).collection("weekly_reports").document(date_range)

    doc_ref.set({
        "company": company_name,
        "date_range": date_range,
        "summary": summary
    })
    print(f"[FIRESTORE] ✅ Data saved for {company_name} – {date_range}")
