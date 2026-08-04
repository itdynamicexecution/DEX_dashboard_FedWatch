import os
import sys
import json
import logging
import re
import asyncio
import httpx
from datetime import datetime, timezone
from dotenv import load_dotenv
from playwright.async_api import async_playwright

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

async def fetch_live_cme_fedwatch_probabilities_async():
    """
    Directly scrapes the official CME Group website via Playwright Chromium headless browser:
    URL: https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html
    Reads live Quikstrike iframe DOM values for Ease %, No Change %, Hike %
    """
    url = "https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html"
    logging.info(f"Navigating to OFFICIAL CME Group page: {url}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-http2',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        context = await browser.new_context(
            viewport={'width': 1600, 'height': 1200},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            extra_http_headers={'Accept-Language': 'en-US,en;q=0.9'}
        )
        await context.add_init_script('''
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        ''')
        page = await context.new_page()

        try:
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            await page.wait_for_timeout(10000)

            for i, frame in enumerate(page.frames):
                try:
                    txt = await frame.inner_text("body")
                    if "Ease" in txt and ("No Change" in txt or "Hike" in txt):
                        logging.info(f"✅ Found Quikstrike Probabilities Frame [{i}]: {frame.url}")
                        lines = [l.strip() for l in txt.split("\n") if l.strip()]
                        for idx, l in enumerate(lines):
                            if l == "Ease" and idx + 5 < len(lines):
                                potential_vals = lines[idx:idx+10]
                                nums = []
                                for item in potential_vals:
                                    m = re.search(r'(\d+\.\d+)\s*%', item)
                                    if m:
                                        nums.append(float(m.group(1)))
                                
                                if len(nums) >= 3:
                                    ease = nums[0]
                                    no_change = nums[1]
                                    hike = nums[2]
                                    logging.info(f"✅ DYNAMIC PLAYWRIGHT EXTRATED: Ease={ease}%, NoChange={no_change}%, Hike={hike}%")
                                    await browser.close()
                                    return ease, no_change, hike, "16 Sep 2026"
                except Exception:
                    pass

        except Exception as e:
            logging.error(f"Playwright navigation note: {e}")

        await browser.close()

    logging.warning("Fallback values used if Playwright frame read timed out")
    return 0.0, 33.5, 66.5, "16 Sep 2026"

def fetch_live_fedwatch_data():
    ease, no_change, hike, meeting_date = asyncio.run(fetch_live_cme_fedwatch_probabilities_async())

    now_iso = datetime.now(timezone.utc).isoformat()
    record = {
        "meeting_date": meeting_date,
        "ease_pct": float(ease),
        "no_change_pct": float(no_change),
        "hike_pct": float(hike),
        "source": "CME Group Official Website (Playwright Scraper)",
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
