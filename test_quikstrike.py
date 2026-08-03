from curl_cffi import requests

def test_quikstrike():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html',
        'Accept': 'application/json, text/plain, */*'
    }

    print("--- 1. Testing CME QuikStrike Widgets ---")
    urls = [
        "https://www.cmegroup.com/CmeApp/mvc/xs/fedwatch/probabilities",
        "https://www.quikstrike.net/User/qv.aspx?pid=27&pf=61&view=fedwatch",
        "https://cmegroup-tools.quikstrike.net/User/qv.aspx?pid=27",
        "https://www.cmegroup.com/CmeApp/mvc/xs/fedwatch/meeting-dates"
    ]

    for url in urls:
        try:
            r = requests.get(url, headers=headers, impersonate='chrome120', timeout=15)
            print(f"URL: {url} -> Status: {r.status_code}, Length: {len(r.text)}")
            if r.status_code == 200:
                print("Snippet:", r.text[:300])
        except Exception as e:
            print("ERR:", e)

if __name__ == '__main__':
    test_quikstrike()
