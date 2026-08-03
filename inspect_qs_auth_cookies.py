from curl_cffi import requests
from bs4 import BeautifulSoup
import json

def inspect_qs_auth_cookies():
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
        
        final_qs_url = r2.url
        print("Final URL:", final_qs_url)
        print("All Cookies:", session.cookies.get_dict())
        
        # Check if there are redirect headers or location
        print("History status codes:", [res.status_code for res in r2.history])
        print("History URLs:", [res.url for res in r2.history])

if __name__ == '__main__':
    inspect_qs_auth_cookies()
