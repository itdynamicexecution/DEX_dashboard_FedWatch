from curl_cffi import requests
from bs4 import BeautifulSoup
import re

def inspect_page():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    url = 'https://www.investing.com/central-banks/fed-rate-monitor'
    r = requests.get(url, headers=headers, impersonate='chrome120', timeout=15)
    
    print("Length:", len(r.text))
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Print all links or iframes
    iframes = soup.find_all('iframe')
    print(f"Total iframes: {len(iframes)}")
    for f in iframes:
        print("Iframe src:", f.get('src'))
        
    # Search for any table or div with class containing rate or fed
    divs = soup.find_all(['div', 'table', 'section'])
    for d in divs:
        text = d.get_text(strip=True)
        if "Ease" in text or "Hike" in text or "No Change" in text:
            print(f"--- Found in {d.name} (class={d.get('class')}) ---")
            print(text[:300])
            break

if __name__ == '__main__':
    inspect_page()
