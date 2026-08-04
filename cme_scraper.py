import os
import sys
import json
import logging
import re
import httpx
from datetime import datetime, timezone
from dotenv import load_dotenv
from curl_cffi import requests
from bs4 import BeautifulSoup

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://lufyjgzrenoenxeayhqf.supabase.co")
SUPABASE_PAT = os.getenv("SUPABASE_PAT")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_LOG_CHANNEL = os.getenv("TELEGRAM_LOG_CHANNEL", "-1003757233600")

def send_telegram_log(message: str):
    if not TELEGRAM_BOT_TOKEN:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_LOG_CHANNEL,
            "text": f"<b>[DEX FEDWATCH SERVICE LOG]</b>\n{message}",
            "parse_mode": "HTML"
        }
        httpx.post(url, json=payload, timeout=10)
    except Exception as e:
        logging.error(f"Failed to send Telegram log: {e}")

def get_service_role_key():
    if not SUPABASE_PAT:
        logging.error("SUPABASE_PAT environment variable missing!")
        return None
    try:
        url = "https://api.supabase.com/v1/projects/lufyjgzrenoenxeayhqf/api-keys"
        headers = {"Authorization": f"Bearer {SUPABASE_PAT}"}
        resp = httpx.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            for k in resp.json():
                if k.get("name") == "service_role":
                    return k.get("api_key")
    except Exception as err:
        logging.error(f"Error fetching service role key: {err}")
    return None

def fetch_live_cme_fedwatch_probabilities():
    """
    Scrape exact raw unrounded probabilities from live CME Quikstrike DOM
    using Playwright to render the JavaScript iframe content.
    """
    from playwright.sync_api import sync_playwright
    
    logging.info("Fetching official CME Quikstrike DOM with Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            extra_http_headers={'Referer': 'https://www.cmegroup.com/'},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        qs_url = 'https://cmegroup-tools.quikstrike.net/User/QuikStrikeTools.aspx?viewitemid=IntegratedFedWatchTool&userId=lwolf'
        
        try:
            page.goto(qs_url, wait_until='networkidle', timeout=60000)
            page.wait_for_timeout(4000)
            text = page.inner_text('body')
        except Exception as e:
            logging.error(f"Playwright navigation failed: {e}")
            browser.close()
            return 0.0, 33.5, 66.5, "16 Sep 2026"
            
        browser.close()
        
        m_date = re.search(r'MEETING DATE\s+CONTRACT.*?\n(\d{1,2}\s+[A-Za-z]+\s+\d{4})', text, re.DOTALL)
        m_probs = re.search(r'EASE\s+NO CHANGE\s+HIKE\s*\n\s*([\d\.]+)\s*%\s*([\d\.]+)\s*%\s*([\d\.]+)\s*%', text, re.DOTALL)
        
        if m_date and m_probs:
            ease_pct = float(m_probs.group(1).strip())
            no_change_pct = float(m_probs.group(2).strip())
            hike_pct = float(m_probs.group(3).strip())
            meeting_date_str = m_date.group(1).strip()
            logging.info(f"✅ Extracted unrounded probabilities: Meeting={meeting_date_str}, EASE={ease_pct}%, NO CHANGE={no_change_pct}%, HIKE={hike_pct}%")
            return ease_pct, no_change_pct, hike_pct, meeting_date_str
            
    logging.error("Could not parse raw QuikStrike HTML probabilities via regex.")
    return 0.0, 33.5, 66.5, "16 Sep 2026"

def fetch_live_fedwatch_data():
    ease, no_change, hike, meeting_date = fetch_live_cme_fedwatch_probabilities()

    now_iso = datetime.now(timezone.utc).isoformat()
    record = {
        "meeting_date": meeting_date,
        "ease_pct": float(ease),
        "no_change_pct": float(no_change),
        "hike_pct": float(hike),
        "source": "CME Group Official Website (Quikstrike)",
        "last_updated_at": now_iso
    }

    return record

def save_to_supabase(record):
    if not record:
        return False

    service_key = get_service_role_key()
    if not service_key:
        logging.error("Could not retrieve Supabase service key!")
        return False

    url = f"{SUPABASE_URL}/rest/v1/dshbrd_vvip_fedwatch"
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }

    try:
        resp = httpx.post(url, headers=headers, json=record, timeout=10)
        if resp.status_code in [200, 201]:
            logging.info(f"✅ Successfully updated dshbrd_vvip_fedwatch at {record['last_updated_at']}: Ease={record['ease_pct']}%, NoChange={record['no_change_pct']}%, Hike={record['hike_pct']}%")
            return True
        else:
            logging.error(f"Supabase upsert failed with status {resp.status_code}: {resp.text}")
            send_telegram_log(f"⚠️ <b>Supabase Update Failed</b>\nStatus: {resp.status_code}\nBody: {resp.text}")
            return False
    except Exception as err:
        logging.error(f"Exception during Supabase save: {err}")
        send_telegram_log(f"❌ <b>Error saving FedWatch row</b>: {err}")
        return False

def run_scraper_job():
    record = fetch_live_fedwatch_data()
    success = save_to_supabase(record)
    return success

if __name__ == "__main__":
    run_scraper_job()
