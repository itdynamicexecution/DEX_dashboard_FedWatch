from curl_cffi import requests
from bs4 import BeautifulSoup
import re

def test_quikstrike_iframe():
    url = "https://cmegroup-tools.quikstrike.net/User/QuikStrikeTools.aspx?viewitemid=IntegratedFedWatchTool"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html'
    }
    
    print("Fetching QuikStrike iframe URL directly with curl_cffi...")
    r = requests.get(url, headers=headers, impersonate='chrome124', timeout=15)
    print("Status:", r.status_code, "Length:", len(r.text))
    
    soup = BeautifulSoup(r.text, 'html.parser')
    text = soup.get_text()
    
    print("\n--- Text Snippet from QuikStrike Tool ---")
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    for l in lines[:40]:
        print(l)
        
    print("\n--- Form / Tables / Spans ---")
    for span in soup.find_all(['span', 'td', 'div', 'tr']):
        stext = span.get_text(strip=True)
        if any(k in stext for k in ["Ease", "Hike", "Unchanged", "No Change", "Probability", "5.25", "5.50", "4.75"]):
            print(f"[{span.name}] -> {stext}")

if __name__ == '__main__':
    test_quikstrike_iframe()
