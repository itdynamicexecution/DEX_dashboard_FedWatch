from curl_cffi import requests
from bs4 import BeautifulSoup
import re

def test_qs_direct():
    url = "https://cmegroup-tools.quikstrike.net/User/QuikStrikeTools.aspx?viewitemid=IntegratedFedWatchTool&insid=236470615&qsid=1d90675c-ae82-44fa-9323-b0ba8f180e7b"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html'
    }
    
    print("Fetching direct Quikstrike page with curl_cffi...")
    r = requests.get(url, headers=headers, impersonate='chrome120', timeout=15)
    print("Status:", r.status_code, "Length:", len(r.text))
    
    soup = BeautifulSoup(r.text, 'html.parser')
    text = soup.get_text()
    
    print("\n--- Inner Text ---")
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    for l in lines[:40]:
        print(l)
        
    print("\n--- Search for Numbers / Percentages ---")
    matches = re.findall(r'(\d+\.\d+%)', r.text)
    print("Percent matches:", matches)

if __name__ == '__main__':
    test_qs_direct()
