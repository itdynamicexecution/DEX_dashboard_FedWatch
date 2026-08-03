from curl_cffi import requests
from bs4 import BeautifulSoup
import re

def test_qs_ajax_postback():
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
        viewstate = qs_soup.find('input', id='__VIEWSTATE')['value']
        viewstategen = qs_soup.find('input', id='__VIEWSTATEGENERATOR')['value']
        eventvalidation = qs_soup.find('input', id='__EVENTVALIDATION')['value']
        form_action = qs_soup.find('form')['action']
        
        if form_action.startswith('.'):
            post_url = "https://cmegroup-tools.quikstrike.net/User" + form_action[1:]
        else:
            post_url = form_action
            
        print("POST URL:", post_url)
        
        # Test event targets
        targets = [
            "smMain|ctl00$MainContent$ucFedWatch",
            "smMain|ctl00$MainContent$btnRefresh",
            "ctl00$MainContent$ucFedWatch",
            "ctl00$MainContent$ucIntegratedFedWatch",
            "smMain|ctl00$MainContent$ucIntegratedFedWatch",
            "smMain|ctl00$MainContent$upFedWatch"
        ]
        
        for target in targets:
            payload = {
                'smMain': target,
                '__EVENTTARGET': target.split('|')[-1],
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': viewstate,
                '__VIEWSTATEGENERATOR': viewstategen,
                '__EVENTVALIDATION': eventvalidation,
                '__ASYNCPOST': 'true'
            }
            
            headers_ajax = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': r2.url,
                'Origin': 'https://cmegroup-tools.quikstrike.net',
                'X-MicrosoftAjax': 'Delta=true',
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            }
            
            r_post = session.post(post_url, headers=headers_ajax, data=payload, timeout=10)
            print(f"Target [{target}] -> Status: {r_post.status_code}, Length: {len(r_post.text)}")
            if len(r_post.text) > 1000 or "Ease" in r_post.text or "Hike" in r_post.text:
                print(f"✅ MATCH FOUND FOR TARGET [{target}]!")
                print("Snippet:", r_post.text[:500])

if __name__ == '__main__':
    test_qs_ajax_postback()
