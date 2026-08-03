from curl_cffi import requests
from bs4 import BeautifulSoup
import re

def get_cme_fedwatch():
    session = requests.Session(impersonate="chrome124")
    
    headers_cme = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    print("1. Loading CME Group FedWatch Tool page...")
    r1 = session.get("https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html", headers=headers_cme, timeout=15)
    print("CME Page Status:", r1.status_code)
    
    soup = BeautifulSoup(r1.text, 'html.parser')
    iframe = soup.find('iframe', src=lambda s: s and 'quikstrike' in s.lower())
    
    if iframe:
        iframe_url = iframe['src']
        print("2. QuikStrike iframe URL found:", iframe_url)
        
        headers_qs = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Referer': 'https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html',
            'Origin': 'https://www.cmegroup.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        
        r2 = session.get(iframe_url, headers=headers_qs, timeout=15)
        print("QuikStrike iframe Status:", r2.status_code, "Length:", len(r2.text))
        print("Final Quikstrike URL:", r2.url)
        
        # Search for WebService / ASMX endpoints in r2.text
        asmx_matches = re.findall(r'(/User/Services/.*?\.asmx/.*?)["\']', r2.text)
        print("Found ASMX WebMethods:", set(asmx_matches))

        # Test calling ASMX WebMethods if found
        for endpoint in set(asmx_matches):
            full_asmx_url = f"https://cmegroup-tools.quikstrike.net{endpoint}"
            print(f"\n3. Testing ASMX WebMethod: {full_asmx_url}")
            try:
                r_asmx = session.post(
                    full_asmx_url,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Referer': r2.url,
                        'Content-Type': 'application/json; charset=UTF-8'
                    },
                    json={},
                    timeout=10
                )
                print("ASMX Status:", r_asmx.status_code, "Snippet:", r_asmx.text[:300])
            except Exception as ex:
                print("ASMX ERR:", ex)

if __name__ == '__main__':
    get_cme_fedwatch()
