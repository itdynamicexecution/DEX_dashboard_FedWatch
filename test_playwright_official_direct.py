import asyncio
from playwright.async_api import async_playwright
import re

async def scrape_official_cme_direct():
    print("Launching Playwright to fetch directly from OFFICIAL CME Group site...")
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
            url = "https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html"
            print(f"Navigating to: {url}")
            resp = await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            print("Response Status:", resp.status if resp else "None")
            await page.wait_for_timeout(12000)

            found = False
            for i, frame in enumerate(page.frames):
                try:
                    txt = await frame.inner_text("body")
                    if "Ease" in txt and ("No Change" in txt or "Hike" in txt):
                        print(f"\n================ SUCCESS! FOUND PROBABILITIES IN FRAME [{i}] ================")
                        print(f"Frame URL: {frame.url}")
                        lines = [l.strip() for l in txt.split("\n") if l.strip()]
                        for l in lines[:40]:
                            print("  ", l)
                        found = True
                        
                        # Extract exact values
                        # Expect lines containing 0.0 %, 33.5 %, 66.5 %
                        nums = re.findall(r'(\d+\.\d+)\s*%', txt)
                        print("\nExtracted Percentage Numbers:", nums)
                except Exception as fe:
                    pass

            if not found:
                print("Could not find probabilities frame. Listing all frame URLs:")
                for i, frame in enumerate(page.frames):
                    print(f"Frame {i}: {frame.url}")

        except Exception as e:
            print("Playwright ERR:", e)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(scrape_official_cme_direct())
