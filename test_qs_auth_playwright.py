from curl_cffi import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import asyncio

async def test_qs_playwright_authenticated():
    session = requests.Session(impersonate="chrome124")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html',
    }
    
    url = "https://cmegroup-tools.quikstrike.net/User/QuikStrikeTools.aspx?viewitemid=FedWatch"
    r = session.get(url, headers=headers, timeout=15)
    authenticated_url = r.url
    print("Authenticated Quikstrike URL:", authenticated_url)
    
    # Extract session cookies
    cookies_list = []
    for k, v in session.cookies.get_dict().items():
        cookies_list.append({'name': k, 'value': v, 'domain': 'cmegroup-tools.quikstrike.net', 'path': '/'})

    print("Launching Playwright on Authenticated URL...")
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
            await context.add_cookies(cookies_list)

        page = await context.new_page()

        page.on('response', lambda resp: print("XHR/Fetch:", resp.status, resp.url) if any(k in resp.url.lower() for k in ['service', 'asmx', 'aspx', 'data', 'json']) else None)

        try:
            await page.goto(authenticated_url, timeout=35000, wait_until="networkidle")
            await page.wait_for_timeout(8000)

            full_text = await page.inner_text("body")
            print("\n--- Playwright QuikStrike Text ---")
            lines = [l.strip() for l in full_text.split("\n") if l.strip()]
            for l in lines[:50]:
                print(l)

        except Exception as e:
            print("Playwright ERR:", e)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_qs_playwright_authenticated())
