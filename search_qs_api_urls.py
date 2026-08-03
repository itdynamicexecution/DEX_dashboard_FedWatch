from curl_cffi import requests
from bs4 import BeautifulSoup
import re

def search_qs_api_urls():
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
        
        # Download all JS files referenced in r2.text
        js_urls = re.findall(r'src=["\'](.*?)["\']', r2.text)
        print("JS URLs found:", js_urls)
        
        for jurl in js_urls:
            if jurl.startswith('/'):
                full_jurl = "https://cmegroup-tools.quikstrike.net" + jurl
            elif jurl.startswith('.'):
                full_jurl = "https://cmegroup-tools.quikstrike.net/User" + jurl[1:]
            else:
                full_jurl = jurl
                
            try:
                r_js = session.get(full_jurl, headers={'Referer': r2.url}, timeout=10)
                if r_js.status_code == 200:
                    endpoints = re.findall(r'["\'](/User/.*?\.ashx|/User/.*?\.asmx/.*?)["\']', r_js.text)
                    if endpoints:
                        print(f"Endpoints found in {full_jurl}:", set(endpoints))
            except Exception as e:
                pass

if __name__ == '__main__':
    search_qs_api_urls()
