from curl_cffi import requests

def main():
    print("Testing curl_cffi on CME Group FedWatch Tool page...")
    try:
        r = requests.get(
            'https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html',
            impersonate='chrome120',
            timeout=15
        )
        print('CME Page Status:', r.status_code)
        print('Page Snippet:', r.text[:600])
        
        if "Probabilities" in r.text or "Target" in r.text or "cme" in r.text.lower():
            print("Successfully bypassed Akamai TLS fingerprint check!")
    except Exception as e:
        print("ERR:", e)

    print("\nTesting MacroMicro CME FedWatch API...")
    try:
        mm_url = "https://www.macromicro.me/api/charts/20121"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Referer": "https://www.macromicro.me/charts/20121/us-cme-fedwatch-rate-probabilities"
        }
        r_mm = requests.get(mm_url, headers=headers, impersonate='chrome120', timeout=15)
        print("MacroMicro Status:", r_mm.status_code)
        if r_mm.status_code == 200:
            data = r_mm.json()
            print("MacroMicro Data Keys:", list(data.keys()))
            chart = data.get("data", {}).get("20121", {})
            series = chart.get("series", [])
            print(f"Total Series: {len(series)}")
            for s in series[:5]:
                print("Series Name:", s.get("name"), "Last Value:", s.get("data", [])[-1] if s.get("data") else None)
    except Exception as e:
        print("MacroMicro ERR:", e)

if __name__ == '__main__':
    main()
