from curl_cffi import requests
from bs4 import BeautifulSoup
import re

def test_qs_sso():
    session = requests.Session(impersonate="chrome124")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html',
        'Origin': 'https://www.cmegroup.com'
    }
    
    login_url = "https://cmegroup-tools.quikstrike.net/Account/Login.aspx?viewitemid=IntegratedFedWatchTool"
    r = session.get(login_url, headers=headers, timeout=15)
    print("Login URL Status:", r.status_code, "Final URL:", r.url)
    
    soup = BeautifulSoup(r.text, 'html.parser')
    print("Page Title:", soup.title.string if soup.title else None)
    
    # Check for text in body
    text = soup.get_text()
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    print("\n--- Body Text ---")
    for l in lines[:30]:
        print(l)

if __name__ == '__main__':
    test_qs_sso()
