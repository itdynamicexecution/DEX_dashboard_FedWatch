from curl_cffi import requests
from bs4 import BeautifulSoup
import re

def test_full_cookie_flow():
    session = requests.Session(impersonate="chrome124")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Referer': 'https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html',
    }
    
    url = "https://cmegroup-tools.quikstrike.net/User/QuikStrikeTools.aspx?viewitemid=FedWatch"
    r = session.get(url, headers=headers, timeout=15)
    
    print("Redirect history:")
    for resp in r.history:
        print(f"  [{resp.status_code}] {resp.url}")
        print("  Cookies set:", resp.cookies.get_dict())
        
    print(f"\nFinal URL: [{r.status_code}] {r.url}")
    print("Final Session Cookies:", session.cookies.get_dict())
    
    soup = BeautifulSoup(r.text, 'html.parser')
    print("\nPage title:", soup.title.string if soup.title else None)
    
    # Check if there is any script containing JSON or data array
    scripts = soup.find_all('script')
    print(f"Total scripts in final page: {len(scripts)}")
    for i, s in enumerate(scripts):
        stext = s.string or s.text
        if stext and ("Target" in stext or "Probability" in stext or "FedWatch" in stext or "chart" in stext.lower()):
            print(f"Script {i} snippet:", stext[:400].strip())

if __name__ == '__main__':
    test_full_cookie_flow()
