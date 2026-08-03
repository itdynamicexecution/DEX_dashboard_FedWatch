import asyncio
from playwright.async_api import async_playwright
import re

async def test_stealth_extract():
    print("Launching Playwright Stealth to extract Quikstrike DOM...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        context = await browser.new_context(
            viewport={'width': 1600, 'height': 1200},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        )
        await context.add_init_script('''
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        ''')

        page = await context.new_page()

        try:
            # Direct navigation to Quikstrike Integrated FedWatch Tool view URL with referrer
            direct_qs = "https://cmegroup-tools.quikstrike.net/User/QuikStrikeTools.aspx?viewitemid=IntegratedFedWatchTool"
            
            await page.set_extra_http_headers({
                'Referer': 'https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html',
                'Origin': 'https://www.cmegroup.com'
            })

            print(f"Navigating to Quikstrike direct URL: {direct_qs}")
            await page.goto(direct_qs, timeout=45000, wait_until="domcontentloaded")
            await page.wait_for_timeout(8000)

            body_text = await page.inner_text("body")
            print("\n--- QUIKSTRIKE BODY TEXT ---")
            lines = [l.strip() for l in body_text.split("\n") if l.strip()]
            for line in lines[:40]:
                print(line)

            # Search for Ease, No Change, Hike values in body_text
            match = re.search(r'Ease\s+No Change\s+Hike\s+([\d\.]+)\s*%\s+([\d\.]+)\s*%\s+([\d\.]+)\s*%', body_text, re.IGNORECASE)
            if match:
                print("\n✅ MATCHED PROBABILITIES IN QUIKSTRIKE DOM:")
                print(f"   Ease: {match.group(1)}%")
                print(f"   No Change: {match.group(2)}%")
                print(f"   Hike: {match.group(3)}%")

        except Exception as e:
            print("ERR:", e)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_stealth_extract())
