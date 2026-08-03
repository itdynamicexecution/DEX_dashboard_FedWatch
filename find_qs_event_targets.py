from curl_cffi import requests
from bs4 import BeautifulSoup
import re

def find_qs_event_targets():
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
        
        qs_url = r2.url
        print("Final URL:", qs_url)
        
        # Search for all control IDs, WebMethods, and UpdatePanel IDs in r2.text
        control_ids = re.findall(r'id=["\'](.*?)["\']', r2.text)
        print("\n--- Control IDs in Page ---")
        for cid in set(control_ids):
            if any(k in cid.lower() for k in ['fedwatch', 'maincontent', 'uc', 'panel', 'update', 'btn', 'lbl']):
                print("Control ID:", cid)
                
        # Search for JS script references
        js_srcs = re.findall(r'src=["\'](.*?)["\']', r2.text)
        print("\n--- JS Script Sources ---")
        for jsrc in set(js_srcs):
            print("JS:", jsrc)

if __name__ == '__main__':
    find_qs_event_targets()
