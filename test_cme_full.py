from curl_cffi import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import asyncio
import re

async def scrape_full_cme_quikstrike():
    session = requests.Session(impersonate="chrome124")
    
    headers_cme = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    print("1. Fetching CME page to obtain session & iframe token...")
    r1 = session.get("https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html", headers=headers_cme, timeout=15)
    
    soup = BeautifulSoup(r1.text, 'html.parser')
    iframe = soup.find('iframe', src=lambda s: s and 'quikstrike' in s.lower())
    
    if not iframe:
        print("Could not find Quikstrike iframe!")
        return

    iframe_url = iframe['src']
    print("2. Following QuikStrike iframe redirect...")
    r2 = session.get(
        iframe_url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html',
            'Origin': 'https://www.cmegroup.com'
        },
        timeout=15
    )
    
    final_qs_url = r2.url
    print("Final Quikstrike Session URL:", final_qs_url)

    # Get session cookies dict
    cookies_list = []
    for k, v in session.cookies.get_dict().items():
        cookies_list.append({'name': k, 'value': v, 'domain': 'cmegroup-tools.quikstrike.net', 'path': '/'})

    print("3. Launching Playwright with active session tokens...")
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
        
        if cookies_list:
            try:
                await context.add_cookies(cookies_list)
            except Exception:
                pass

        page = await context.new_page()

        page.on('response', lambda resp: print("API Response:", resp.status, resp.url) if any(k in resp.url.lower() for k in ['service', 'asmx', 'get', 'prob', 'fedwatch', 'json']) else None)

        await page.goto(final_qs_url, timeout=35000, wait_until="networkidle")
        await page.wait_for_timeout(8000)

        body_text = await page.inner_text("body")
        print("\n--- Inner Text Sample ---")
        lines = [l.strip() for l in body_text.split("\n") if l.strip()]
        for l in lines[:50]:
            print(l)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(scrape_full_cme_quikstrike())
