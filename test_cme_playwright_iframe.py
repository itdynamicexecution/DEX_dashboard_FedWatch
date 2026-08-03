import asyncio
from playwright.async_api import async_playwright
import re

async def test_full_playwright_iframe():
    print("Navigating to CME FedWatch Tool official page via Playwright...")
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
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
            }
        )
        
        await context.add_init_script('''
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        ''')

        page = await context.new_page()

        try:
            # Bypass Akamai protocol error by setting domcontentloaded
            resp = await page.goto('https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html', timeout=45000, wait_until='domcontentloaded')
            print("CME Page Status:", resp.status if resp else "None")
            await page.wait_for_timeout(10000)

            print(f"\n--- Total Frames Loaded: {len(page.frames)} ---")
            for i, frame in enumerate(page.frames):
                url = frame.url
                print(f"Frame [{i}]: {url}")
                try:
                    text = await frame.inner_text("body")
                    if any(k in text for k in ["Target Rate", "Probability", "Meeting Date", "Ease", "Hike", "Unchanged", "525-550"]):
                        print(f"✅ FOUND FEDWATCH DATA IN FRAME [{i}]:")
                        lines = [l.strip() for l in text.split("\n") if l.strip()]
                        for l in lines[:40]:
                            print(l)
                except Exception as fe:
                    print(f"Frame [{i}] read note: {fe}")

        except Exception as e:
            print("ERR:", e)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_full_playwright_iframe())
