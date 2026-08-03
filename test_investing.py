from curl_cffi import requests
from bs4 import BeautifulSoup
import re

def inspect_page():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    url = 'https://www.investing.com/central-banks/fed-rate-monitor'
    r = requests.get(url, headers=headers, impersonate='chrome120', timeout=15)
    
    soup = BeautifulSoup(r.text, 'html.parser')
    text = soup.get_text()
    
    # Print lines containing % or probabilities
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    print(f"Total lines: {len(lines)}")
    
    for i, line in enumerate(lines):
        if any(k in line.lower() for k in ["ease", "hike", "no change", "probability", "meeting", "5.25", "5.50", "4.75"]):
            print(f"Line {i}: {line}")

if __name__ == '__main__':
    inspect_page()
