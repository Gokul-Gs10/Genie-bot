from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from backend.chatbot import ask_ai
from backend.logo_scraper import fetch_and_save_logo
from backend.firebase import store_report_data
from backend.generate_report import generate_pdf, calculate_last_week_range
import os

app = FastAPI()

# -------------------- CORS Middleware --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ✅ Set specific domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- Pydantic Schemas --------------------

class Summary(BaseModel):
    reach: int
    views: int
    new_follows: int
    unfollows: int
    views_from_non_followers_percent: float

class Post(BaseModel):
    url: str
    date: str
    likes: int
    views: int

class Reel(BaseModel):
    url: str
    date: str
    duration: str
    views: int
    likes: int

class ReportData(BaseModel):
    company_name: str
    website: str = ""
    date_range: str = ""
    posts: list[Post]
    reels: list[Reel]
    summary: Summary
    startgenie_logo: str = "backend/static/logo/startgenie.png"
    client_logo: str = ""

class ChatRequest(BaseModel):
    prompt: str
    company_name: str

# -------------------- Routes --------------------

@app.get("/")
def home():
    return {"message": "🚀 SmartGenie backend is up and running!"}

@app.post("/generate_report")
async def generate_report(data: ReportData):
    # 🔄 Auto-fetch logo
    if not data.client_logo and data.website:
        logo_path = fetch_and_save_logo(data.website)
        data.client_logo = logo_path if logo_path else "backend/static/logo/client_logo.png"

    # ⏱️ Auto-generate date range if missing
    if not data.date_range:
        data.date_range = calculate_last_week_range()

    # 📝 Generate report
    pdf_path = generate_pdf(data.dict())

    # 🔐 Store summary to Firebase
    store_report_data(data.company_name, data.date_range, data.summary.dict())

    return JSONResponse({
        "message": "✅ Report generated successfully!",
        "preview_url": "/preview_report",
        "download_url": "/download_report"
    })

@app.get("/preview_report")
async def preview_report():
    return FileResponse("backend/output/report.pdf", media_type="application/pdf")

@app.get("/download_report")
async def download_report():
    return FileResponse(
        "backend/output/report.pdf",
        media_type="application/pdf",
        filename="SmartGenie_Weekly_Report.pdf"
    )

@app.post("/ask_ai")
async def ask_ai_route(data: ChatRequest):
    response = ask_ai(data.prompt, data.company_name)
    return {"response": response}
