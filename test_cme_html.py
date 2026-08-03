from curl_cffi import requests
from bs4 import BeautifulSoup

def inspect_cme_html():
    url = "https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    print("Fetching CME Group FedWatch page with curl_cffi...")
    r = requests.get(url, headers=headers, impersonate='chrome124', timeout=15)
    print("Status:", r.status_code, "Length:", len(r.text))
    
    soup = BeautifulSoup(r.text, 'html.parser')
    
    print("\n--- IFRAMES ---")
    for f in soup.find_all('iframe'):
        print("Iframe SRC:", f.get('src'))
        
    print("\n--- SCRIPTS WITH URLS ---")
    for s in soup.find_all('script'):
        src = s.get('src')
        if src and any(k in src.lower() for k in ['fedwatch', 'quikstrike', 'tools', 'cme']):
            print("Script SRC:", src)
            
    print("\n--- DIVS/SECTIONS WITH CME DATA ---")
    for d in soup.find_all(['div', 'iframe', 'object', 'embed']):
        id_val = d.get('id')
        class_val = d.get('class')
        if id_val or class_val:
            if any(k in str(id_val).lower() or k in str(class_val).lower() for k in ['fedwatch', 'quikstrike', 'chart', 'widget', 'main']):
                print(f"Element: {d.name}, id={id_val}, class={class_val}")

if __name__ == '__main__':
    inspect_cme_html()
