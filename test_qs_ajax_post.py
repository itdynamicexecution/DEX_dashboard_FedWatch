from curl_cffi import requests
from bs4 import BeautifulSoup
import re

def test_qs_ajax_post():
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
        soup_qs = BeautifulSoup(r2.text, 'html.parser')
        
        viewstate = soup_qs.find('input', id='__VIEWSTATE')['value']
        generator = soup_qs.find('input', id='__VIEWSTATEGENERATOR')['value']
        validation = soup_qs.find('input', id='__EVENTVALIDATION')['value']
        
        # ASP.NET ScriptManager Delta AJAX Payload
        payload = {
            'smMain': 'smMain|smMain',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': generator,
            '__EVENTVALIDATION': validation,
            '__ASYNCPOST': 'true'
        }
        
        headers_ajax = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': qs_url,
            'X-MicrosoftAjax': 'Delta=true',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        
        print("Executing ASP.NET ScriptManager AJAX request...")
        r_ajax = session.post(qs_url, headers=headers_ajax, data=payload, timeout=15)
        print("AJAX Status:", r_ajax.status_code, "Length:", len(r_ajax.text))
        print("AJAX Snippet:", r_ajax.text[:500])
        
        # Search for percentages or probability terms in r_ajax.text
        matches = re.findall(r'(\d+\.\d+%)', r_ajax.text)
        print("Percent matches in AJAX response:", matches)

if __name__ == '__main__':
    test_qs_ajax_post()
