from curl_cffi import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import asyncio
import re

async def get_live_cme_probabilities():
    print("1. Fetching CME Group FedWatch page via curl_cffi...")
    url = "https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html"
    r = requests.get(url, impersonate='chrome124', timeout=15)
    print("CME Page Status:", r.status_code)
    
    soup = BeautifulSoup(r.text, 'html.parser')
    iframe_src = None
    for f in soup.find_all('iframe'):
        src = f.get('src')
        if src and 'quikstrike' in src.lower():
            iframe_src = src
            print("Found Quikstrike iframe URL:", iframe_src)
            break

    if iframe_src:
        print("\n2. Navigating to Quikstrike iframe URL via Playwright...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-blink-features=AutomationControlled']
            )
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                extra_http_headers={
                    'Referer': 'https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html',
                    'Origin': 'https://www.cmegroup.com'
                }
            )
            page = await context.new_page()

            # Listen for WebMethods / JSON responses
            captured_json = []
            async def on_resp(resp):
                if 'json' in resp.url.lower() or 'webmethod' in resp.url.lower() or 'get' in resp.url.lower():
                    try:
                        ct = resp.headers.get('content-type', '')
                        if 'json' in ct or 'text' in ct:
                            txt = await resp.text()
                            if any(k in txt for k in ['Ease', 'Hike', 'Unchanged', 'Probability', '5.25', '5.50', 'EaseProb']):
                                captured_json.append((resp.url, txt))
                    except Exception:
                        pass

            page.on('response', on_resp)

            await page.goto(iframe_src, timeout=30000, wait_until="networkidle")
            await page.wait_for_timeout(8000)

            full_text = await page.inner_text("body")
            print("\n--- Inner Text Result ---")
            lines = [l.strip() for l in full_text.split("\n") if l.strip()]
            for l in lines[:40]:
                print(l)

            print(f"\n--- Captured {len(captured_json)} JSON payloads ---")
            for u, t in captured_json[:5]:
                print(f"URL: {u}\nPayload: {t[:400]}\n")

            await browser.close()

if __name__ == '__main__':
    asyncio.run(get_live_cme_probabilities())
