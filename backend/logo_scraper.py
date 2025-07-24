import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

def fetch_logo_url(website_url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(website_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
    except Exception as e:
        print(f"[LOGO FETCH ERROR] {e}")
        return None

    selectors = [
        'link[rel="icon"]', 'link[rel="shortcut icon"]',
        'link[rel="apple-touch-icon"]',
        'img[src*="logo"]', 'img[alt*="logo"]', 'img[class*="logo"]'
    ]

    for selector in selectors:
        tag = soup.select_one(selector)
        if tag:
            logo_src = tag.get('href') or tag.get('src')
            if logo_src:
                return urljoin(website_url, logo_src)
    return None

def download_logo(logo_url, output_path="backend/static/logo/client_logo.png"):
    try:
        response = requests.get(logo_url, stream=True, timeout=10)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"[LOGO SAVED] {output_path}")
        return output_path
    except Exception as e:
        print(f"[DOWNLOAD ERROR] {e}")
        return None

def fetch_and_save_logo(website_url):
    logo_url = fetch_logo_url(website_url)
    if not logo_url:
        print("[LOGO SCRAPER] No logo found.")
        return None
    return download_logo(logo_url)
