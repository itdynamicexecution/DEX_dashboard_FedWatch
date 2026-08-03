from curl_cffi import requests
from bs4 import BeautifulSoup
import re

def parse_investing_fedwatch():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    url = 'https://www.investing.com/central-banks/fed-rate-monitor'
    print("Parsing Investing.com Fed Rate Monitor table...")
    try:
        r = requests.get(url, headers=headers, impersonate='chrome120', timeout=15)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            tables = soup.find_all('table')
            print(f"Total tables found: {len(tables)}")
            
            for idx, tbl in enumerate(tables):
                text = tbl.get_text()
                if any(k in text for k in ["Ease", "Hike", "No Change", "Probability", "Meeting", "Target"]):
                    print(f"\n--- Table {idx} ---")
                    for row in tbl.find_all('tr'):
                        cols = [c.get_text(strip=True) for c in row.find_all(['td', 'th'])]
                        if cols:
                            print(cols)

            # Search text for percentages
            matches = re.findall(r'(\bEase\b|\bHike\b|\bNo Change\b|\bUnchanged\b).*?(\d+\.\d+%)', r.text, re.IGNORECASE)
            print("\nRegex matches:", matches[:10])

    except Exception as e:
        print("ERR:", e)

if __name__ == '__main__':
    parse_investing_fedwatch()
