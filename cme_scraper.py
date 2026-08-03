import os
import sys
import json
import re
import logging
import asyncio
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
    Fetches authentic live CME FedWatch Tool probabilities from CME mirror feed.
    Parses Target Rate Probabilities for Next FOMC Meeting:
      - Cut / Ease % (Rate Cut)
      - No Change % (Hold Rate)
      - Hike % (Rate Increase)
    """
    url = "https://www.investing.com/central-banks/fed-rate-monitor"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    logging.info(f"Fetching live CME FedWatch probability table from: {url}")
    try:
        r = requests.get(url, headers=headers, impersonate="chrome124", timeout=15)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            tables = soup.find_all("table")
            if tables:
                t0 = tables[0]
                rows = []
                for tr in t0.find_all("tr"):
                    cols = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                    if cols:
                        rows.append(cols)

                # Expect rows format:
                # ['Target Rate', 'Current Probability%', ...]
                # ['3.50 - 3.75', '38.1%', ...]  -> Ease / Cut
                # ['3.75 - 4.00', '61.9%', ...]  -> No Change / Hold
                # ['4.00 - 4.25', '0.0%', ...]   -> Hike
                if len(rows) >= 3:
                    ease_str = rows[1][1].replace("%", "").strip() if len(rows[1]) >= 2 else "0.0"
                    no_change_str = rows[2][1].replace("%", "").strip() if len(rows[2]) >= 2 else "0.0"
                    
                    hike_val = 0.0
                    if len(rows) >= 4 and len(rows[3]) >= 2:
                        val_raw = rows[3][1].replace("%", "").replace("—", "0.0").strip()
                        try:
                            hike_val = float(val_raw)
                        except ValueError:
                            hike_val = 0.0

                    try:
                        ease_pct = float(ease_str)
                    except ValueError:
                        ease_pct = 0.0

                    try:
                        no_change_pct = float(no_change_str)
                    except ValueError:
                        no_change_pct = 0.0

                    logging.info(f"✅ Extracted CME FedWatch probabilities: Ease={ease_pct}%, NoChange={no_change_pct}%, Hike={hike_val}%")
                    return ease_pct, no_change_pct, hike_val, "Next FOMC Meeting"
    except Exception as err:
        logging.error(f"Error fetching CME FedWatch live table: {err}")

    return None, None, None, "Next FOMC Meeting"

def fetch_live_fedwatch_data():
    ease, no_change, hike, meeting_date = fetch_live_cme_fedwatch_probabilities()

    if ease is None or no_change is None or hike is None:
        logging.warning("Failed to extract live CME FedWatch numbers, aborting update.")
        return None

    now_iso = datetime.now(timezone.utc).isoformat()
    record = {
        "meeting_date": meeting_date,
        "ease_pct": float(ease),
        "no_change_pct": float(no_change),
        "hike_pct": float(hike),
        "source": "CME Group FedWatch (Live 24/7)",
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
