import asyncio
from playwright.async_api import async_playwright

async def main():
    print("Navigating to CME FedWatch Tool page via Playwright...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-blink-features=AutomationControlled']
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
            await page.goto("https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html", timeout=60000, wait_until="domcontentloaded")
            await page.wait_for_timeout(10000)
            
            await page.screenshot(path="/root/DEX_dashboard_FedWatch/cme_page.png", full_page=False)
            print("Saved /root/DEX_dashboard_FedWatch/cme_page.png")

            for i, frame in enumerate(page.frames):
                try:
                    await frame.screenshot(path=f"/root/DEX_dashboard_FedWatch/frame_{i}.png")
                    print(f"Saved /root/DEX_dashboard_FedWatch/frame_{i}.png")
                    txt = await frame.inner_text("body")
                    if any(k in txt for k in ["Target Rate", "Probability", "Meeting", "Ease", "Hike", "5.25"]):
                        print(f"--- MATCHING TEXT IN FRAME {i} ---")
                        lines = [l.strip() for l in txt.split("\n") if l.strip()]
                        for line in lines[:30]:
                            print(line)
                except Exception as fe:
                    print(f"Frame {i} note: {fe}")

        except Exception as e:
            print("ERR:", e)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
