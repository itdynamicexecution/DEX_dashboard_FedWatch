from curl_cffi import requests
from bs4 import BeautifulSoup
import re
import json

def parse_quikstrike_hidden_fields():
    session = requests.Session(impersonate="chrome124")
    
    headers_cme = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    r1 = session.get("https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html", headers=headers_cme, timeout=15)
    soup = BeautifulSoup(r1.text, 'html.parser')
    iframe = soup.find('iframe', src=lambda s: s and 'quikstrike' in s.lower())
    
    if iframe:
        iframe_url = iframe['src']
        r2 = session.get(
            iframe_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html',
            },
            timeout=15
        )
        
        print("Final URL:", r2.url)
        soup_qs = BeautifulSoup(r2.text, 'html.parser')
        
        print("\n--- Hidden Inputs in QuikStrike Page ---")
        for inp in soup_qs.find_all('input'):
            name = inp.get('name') or inp.get('id')
            val = inp.get('value', '')
            if val and len(val) > 0:
                print(f"Input: {name} -> {val[:150]}")
                
        print("\n--- Inline Scripts with JSON / Data ---")
        for s in soup_qs.find_all('script'):
            stext = s.string or s.text
            if stext and any(k in stext.lower() for k in ['prob', 'fedwatch', 'target', 'meeting', 'data', 'var ']):
                print("Script snippet:", stext[:300].strip())
                print("="*40)

if __name__ == '__main__':
    parse_quikstrike_hidden_fields()
