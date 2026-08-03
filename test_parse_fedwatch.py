from curl_cffi import requests
from bs4 import BeautifulSoup
import re

def test_parse_fedwatch_view():
    session = requests.Session(impersonate="chrome124")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html',
    }
    
    url = "https://cmegroup-tools.quikstrike.net/User/QuikStrikeTools.aspx?viewitemid=FedWatch"
    r = session.get(url, headers=headers, timeout=15)
    print("FedWatch View Status:", r.status_code, "Final URL:", r.url)
    
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Print all inputs, script tags, and tables
    print("\n--- Hidden & Text Inputs ---")
    for inp in soup.find_all('input'):
        print(f"Input {inp.get('name') or inp.get('id')} = {inp.get('value', '')[:100]}")
        
    print("\n--- Tables ---")
    tables = soup.find_all('table')
    print(f"Total tables: {len(tables)}")
    for i, t in enumerate(tables):
        print(f"Table {i} Snippet:", t.get_text(strip=True)[:300])
        
    print("\n--- Script text containing data ---")
    for s in soup.find_all('script'):
        stext = s.string or s.text
        if stext and len(stext) > 50:
            print("Script:", stext[:400].strip())
            print("="*40)

if __name__ == '__main__':
    test_parse_fedwatch_view()
