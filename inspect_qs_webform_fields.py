from curl_cffi import requests
from bs4 import BeautifulSoup
import re

def inspect_qs_webform_fields():
    session = requests.Session(impersonate="chrome124")
    
    headers_cme = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    }
    
    r1 = session.get("https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html", headers=headers_cme, timeout=15)
    soup = BeautifulSoup(r1.text, 'html.parser')
    iframe = soup.find('iframe', src=lambda s: s and 'quikstrike' in s.lower())
    
    if iframe:
        iframe_src = iframe['src']
        r2 = session.get(
            iframe_src,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'Referer': 'https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html',
            },
            timeout=15
        )
        
        qs_soup = BeautifulSoup(r2.text, 'html.parser')
        form = qs_soup.find('form')
        print("Form Action:", form.get('action') if form else None)
        
        inputs = qs_soup.find_all('input')
        print(f"\n--- All Form Inputs ({len(inputs)}) ---")
        for inp in inputs:
            print(f"Input: name='{inp.get('name')}' id='{inp.get('id')}' type='{inp.get('type')}' value='{inp.get('value', '')[:80]}'")

if __name__ == '__main__':
    inspect_qs_webform_fields()
