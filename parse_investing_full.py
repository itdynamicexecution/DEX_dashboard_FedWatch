from curl_cffi import requests
from bs4 import BeautifulSoup
import re
import json

def parse_investing_full():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    url = 'https://www.investing.com/central-banks/fed-rate-monitor'
    print("Fetching Investing.com Fed Rate Monitor with curl_cffi...")
    r = requests.get(url, headers=headers, impersonate='chrome124', timeout=15)
    print("Status:", r.status_code, "Length:", len(r.text))
    
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # 1. Search all tables
    tables = soup.find_all('table')
    print(f"\n--- Total Tables: {len(tables)} ---")
    for i, t in enumerate(tables):
        rows = []
        for tr in t.find_all('tr'):
            cols = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
            if cols:
                rows.append(cols)
        print(f"Table {i} rows ({len(rows)}):")
        for r in rows[:10]:
            print("  ", r)

    # 2. Search all script tags with JSON
    print("\n--- Searching for script tags with JSON data ---")
    for s in soup.find_all('script'):
        stext = s.string or s.text
        if stext and ('probability' in stext.lower() or 'fedrate' in stext.lower() or 'meeting' in stext.lower()):
            print("Found matching script:", stext[:400].strip())
            print("="*40)

if __name__ == '__main__':
    parse_investing_full()
