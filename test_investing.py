from curl_cffi import requests
from bs4 import BeautifulSoup

def test_investing_fedwatch():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    url = 'https://www.investing.com/central-banks/fed-rate-monitor'
    print("Testing Investing.com Fed Rate Monitor with curl_cffi...")
    try:
        r = requests.get(url, headers=headers, impersonate='chrome120', timeout=15)
        print("Status:", r.status_code, "Length:", len(r.text))
        if r.status_code == 200:
            print("Snippet:", r.text[:500])
            if "Fed Rate Monitor" in r.text or "Ease" in r.text or "Hike" in r.text or "Probability" in r.text or "Current" in r.text:
                print("SUCCESS: Found Fed Rate Monitor content!")
    except Exception as e:
        print("ERR:", e)

if __name__ == '__main__':
    test_investing_fedwatch()
