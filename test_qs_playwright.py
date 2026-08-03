import asyncio
import json
from playwright.async_api import async_playwright

async def test_qs_ajax():
    print("Testing Quikstrike AJAX interception...")
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

        ajax_data = []
        async def on_response(resp):
            url = resp.url
            if any(k in url.lower() for k in ['aspx', 'webmethod', 'getdata', 'probabilities', 'fedwatch', 'json', 'service']):
                try:
                    text = await resp.text()
                    ajax_data.append((url, resp.status, text))
                except Exception:
                    pass

        page.on('response', on_response)

        qs_url = "https://cmegroup-tools.quikstrike.net/User/QuikStrikeTools.aspx?viewitemid=IntegratedFedWatchTool"
        try:
            resp = await page.goto(qs_url, timeout=35000, wait_until="networkidle")
            await page.wait_for_timeout(8000)

            print(f"\n--- Intercepted {len(ajax_data)} AJAX responses ---")
            for url, status, text in ajax_data:
                print(f"[{status}] {url}\n  Length: {len(text)}, Sample: {text[:250]}\n")

            full_text = await page.inner_text("body")
            print("--- Full Body Text ---")
            print(full_text[:1500])

        except Exception as e:
            print("ERR:", e)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_qs_ajax())
