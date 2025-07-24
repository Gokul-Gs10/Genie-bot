from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from datetime import datetime, timedelta
import os

BASE_TEMPLATE_DIR = "backend/templates"
DEFAULT_OUTPUT_PATH = "backend/output/report.pdf"
DEFAULT_STARTGENIE_LOGO = "backend/static/logo/startgenie.png"
DEFAULT_CLIENT_LOGO = "backend/static/logo/client_logo.png"

def calculate_last_week_range():
    today = datetime.today()
    last_monday = today - timedelta(days=today.weekday() + 7)
    start_date = last_monday + timedelta(days=1)  # Tuesday
    end_date = last_monday + timedelta(days=6)    # Sunday
    return f"{start_date.strftime('%b %d')} – {end_date.strftime('%b %d')}"

def generate_pdf(data: dict, output_path=DEFAULT_OUTPUT_PATH):
    if not data.get("date_range"):
        data["date_range"] = calculate_last_week_range()

    data["startgenie_logo"] = data.get("startgenie_logo", DEFAULT_STARTGENIE_LOGO)
    data["client_logo"] = data.get("client_logo", DEFAULT_CLIENT_LOGO)

    env = Environment(loader=FileSystemLoader(BASE_TEMPLATE_DIR))
    template = env.get_template("report_template.html")

    html_out = template.render(data)
    HTML(string=html_out, base_url=os.getcwd()).write_pdf(output_path)
    return output_path
