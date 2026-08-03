import asyncio
from playwright.async_api import async_playwright

async def test_qs_with_referrer():
    print("Testing Quikstrike with valid CME Referrer header...")
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
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            extra_http_headers={
                'Referer': 'https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html',
                'Origin': 'https://www.cmegroup.com'
            }
        )
        page = await context.new_page()

        api_urls = []
        page.on('response', lambda r: api_urls.append((r.url, r.status)) if any(k in r.url.lower() for k in ['quikstrike', 'api', 'fedwatch', 'json', 'data', 'probabilities']) else None)

        qs_url = "https://cmegroup-tools.quikstrike.net/User/QuikStrikeTools.aspx?viewitemid=IntegratedFedWatchTool"
        try:
            resp = await page.goto(qs_url, timeout=30000, wait_until="networkidle")
            print("Status:", resp.status if resp else "None")
            await page.wait_for_timeout(6000)

            print(f"\n--- Intercepted {len(api_urls)} API URLs ---")
            for url, status in api_urls[:20]:
                print(f"[{status}] {url}")

            text = await page.inner_text("body")
            print("\n--- Inner Text Sample ---")
            print(text[:1200])

        except Exception as e:
            print("ERR:", e)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_qs_with_referrer())
