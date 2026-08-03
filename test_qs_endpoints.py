from curl_cffi import requests
from bs4 import BeautifulSoup
import json

def test_qs_webmethods():
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
        
        final_url = r2.url
        print("Final Session URL:", final_url)
        
        # Candidate WebMethods
        endpoints = [
            "https://cmegroup-tools.quikstrike.net/User/Services/FedWatchService.asmx/GetProbabilities",
            "https://cmegroup-tools.quikstrike.net/User/Services/FedWatchService.asmx/GetMeetingDates",
            "https://cmegroup-tools.quikstrike.net/User/Services/FedWatchService.asmx/GetTargetRateProbabilities",
            "https://cmegroup-tools.quikstrike.net/User/Services/QuikStrikeService.asmx/GetToolView",
            "https://cmegroup-tools.quikstrike.net/User/Services/FedWatchService.asmx/GetFedWatchProbabilities"
        ]
        
        for ep in endpoints:
            try:
                r_ep = session.post(
                    ep,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Referer': final_url,
                        'Content-Type': 'application/json; charset=UTF-8'
                    },
                    json={},
                    timeout=10
                )
                print(f"Endpoint: {ep} -> Status: {r_ep.status_code}")
                if r_ep.status_code == 200:
                    print("SUCCESS PAYLOAD:", r_ep.text[:500])
            except Exception as e:
                print(f"ERR for {ep}: {e}")

if __name__ == '__main__':
    test_qs_webmethods()
