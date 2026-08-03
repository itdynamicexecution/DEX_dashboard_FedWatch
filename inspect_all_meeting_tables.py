from curl_cffi import requests
from bs4 import BeautifulSoup

def inspect_all_tables():
    url = "https://www.investing.com/central-banks/fed-rate-monitor"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    }
    
    r = requests.get(url, headers=headers, impersonate="chrome124", timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Search for all meeting date headers and tables
    headers_tags = soup.find_all(['h2', 'h3', 'h4', 'div', 'span'])
    print("--- Searching for FOMC Meeting Date Headers ---")
    for tag in headers_tags:
        txt = tag.get_text(strip=True)
        if any(month in txt for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]) and ("202" in txt or "Meeting" in txt or "FOMC" in txt):
            if len(txt) < 100:
                print("Header:", txt)

    tables = soup.find_all('table')
    print(f"\n--- Total Tables: {len(tables)} ---")
    for i, t in enumerate(tables):
        prev_sibling = t.find_previous(['h2', 'h3', 'h4', 'div', 'span'])
        prev_txt = prev_sibling.get_text(strip=True) if prev_sibling else "Unknown"
        rows = []
        for tr in t.find_all('tr'):
            cols = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
            if cols:
                rows.append(cols)
        if len(rows) > 1 and "Target Rate" in rows[0]:
            print(f"\n================ Table {i} (Header: {prev_txt[:50]}) ================")
            for r in rows:
                print("  ", r)

if __name__ == '__main__':
    inspect_all_tables()
