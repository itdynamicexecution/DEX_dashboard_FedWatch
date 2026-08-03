from curl_cffi import requests
from bs4 import BeautifulSoup
import re
import json

def test_cme_direct_official():
    session = requests.Session(impersonate="chrome124")
    
    headers_cme = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    print("1. Fetching official CME Group page: https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html")
    r1 = session.get("https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html", headers=headers_cme, timeout=20)
    print("   CME Status:", r1.status_code)
    
    soup = BeautifulSoup(r1.text, 'html.parser')
    iframe = soup.find('iframe', src=lambda s: s and 'quikstrike' in s.lower())
    
    if iframe:
        iframe_src = iframe['src']
        print("\n2. Found Quikstrike iframe URL:", iframe_src)
        
        headers_qs = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Referer': 'https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        r2 = session.get(iframe_src, headers=headers_qs, timeout=20)
        print("   Quikstrike Status:", r2.status_code, "Final URL:", r2.url)
        
        # Check if Quikstrike HTML contains Probabilities table or WebForm hidden fields
        qs_soup = BeautifulSoup(r2.text, 'html.parser')
        
        # Search all script content or table tags
        print("\n3. Searching Quikstrike HTML tables:")
        qs_tables = qs_soup.find_all('table')
        print(f"   Total tables found: {len(qs_tables)}")
        for i, t in enumerate(qs_tables):
            txt = t.get_text(" | ", strip=True)
            if "Ease" in txt or "Hike" in txt or "Change" in txt or "Probabilities" in txt:
                print(f"   MATCHING TABLE [{i}]:", txt)

        # Search script tags for data arrays or JSON
        print("\n4. Searching Quikstrike script tags for data:")
        for s in qs_soup.find_all('script'):
            stext = s.string or s.text
            if stext and ("Ease" in stext or "No Change" in stext or "FedWatch" in stext or "probabilities" in stext.lower()):
                print("   Found matching script text:", stext[:400].strip())

if __name__ == '__main__':
    test_cme_direct_official()
