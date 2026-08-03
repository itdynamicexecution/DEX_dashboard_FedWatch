import asyncio
import re
import httpx
from playwright.async_api import async_playwright

async def get_real_cme_data():
    print("Navigating to CME FedWatch Tool official page...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-http2',
                '--disable-blink-features=AutomationControlled',
                '--ignore-certificate-errors'
            ]
        )
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        )
        
        await context.add_init_script('''
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        ''')
        
        page = await context.new_page()
        
        cme_url = "https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html"
        try:
            resp = await page.goto(cme_url, timeout=60000, wait_until="domcontentloaded")
            print("CME Page Status:", resp.status if resp else "None")
            await page.wait_for_timeout(8000)
            
            title = await page.title()
            print("Page Title:", title)
            
            # Print frames and content
            for i, frame in enumerate(page.frames):
                try:
                    text = await frame.inner_text("body")
                    if any(k in text for k in ["Target Rate", "Probability", "Meeting Date", "Ease", "Hike", "Unchanged", "525-550"]):
                        print(f"--- Matching Frame {i}: {frame.url} ---")
                        print(text[:800])
                except Exception as fe:
                    pass

        except Exception as e:
            print("Navigation Error:", e)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(get_real_cme_data())
