from curl_cffi import requests
from bs4 import BeautifulSoup

def test_qs_views():
    session = requests.Session(impersonate="chrome124")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html',
    }
    
    views = [
        "FedWatch",
        "FedWatchTool",
        "TargetRate",
        "IntegratedFedWatch",
        "CMEFedWatch"
    ]
    
    for v in views:
        url = f"https://cmegroup-tools.quikstrike.net/User/QuikStrikeTools.aspx?viewitemid={v}"
        try:
            r = session.get(url, headers=headers, timeout=15)
            print(f"View [{v}] -> Status: {r.status_code}, Final URL: {r.url}")
            if "ErrorPage" not in r.url:
                print("SUCCESS! Final URL:", r.url)
                print("Snippet:", r.text[:400])
        except Exception as e:
            print(f"View [{v}] ERR: {e}")

if __name__ == '__main__':
    test_qs_views()
