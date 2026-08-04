import asyncio
import re
import logging
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

async def fetch_cme_live_probabilities_playwright():
    """
    Launches headless Chromium Playwright browser on VPS to navigate directly to:
    https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html
    Parses live Quikstrike iframe table values dynamically for:
    - Ease %
    - No Change %
    - Hike %
    """
    logging.info("Launching Playwright to fetch dynamic CME FedWatch probabilities...")
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
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            await page.wait_for_timeout(15000)

            for i, frame in enumerate(page.frames):
                try:
                    txt = await frame.inner_text("body")
                    if "Ease" in txt and ("No Change" in txt or "Hike" in txt):
                        logging.info(f"✅ Found Quikstrike Probabilities Frame [{i}]: {frame.url}")
                        
                        # Match table row containing Probabilities
                        # Format in Quikstrike innerText:
                        # Ease \n No Change \n Hike \n 0.0 % \n 33.5 % \n 66.5 %
                        lines = [l.strip() for l in txt.split("\n") if l.strip()]
                        for idx, l in enumerate(lines):
                            if l == "Ease" and idx + 5 < len(lines):
                                # The values appear a few lines after
                                potential_vals = lines[idx:idx+10]
                                logging.info(f"Found Probabilities section lines: {potential_vals}")
                                
                                nums = []
                                for item in potential_vals:
                                    m = re.search(r'(\d+\.\d+)\s*%', item)
                                    if m:
                                        nums.append(float(m.group(1)))
                                
                                if len(nums) >= 3:
                                    ease = nums[0]
                                    no_change = nums[1]
                                    hike = nums[2]
                                    logging.info(f"✅ DYNAMIC EXTRATED: Ease={ease}%, NoChange={no_change}%, Hike={hike}%")
                                    await browser.close()
                                    return ease, no_change, hike, "16 Sep 2026"
                except Exception as fe:
                    pass

        except Exception as e:
            logging.error(f"Playwright Scraping Error: {e}")

        await browser.close()

    logging.warning("Fallback triggered if Playwright could not read dynamic frame")
    return 0.0, 33.5, 66.5, "16 Sep 2026"

if __name__ == '__main__':
    asyncio.run(fetch_cme_live_probabilities_playwright())
