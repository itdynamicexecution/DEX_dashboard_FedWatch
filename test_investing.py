from curl_cffi import requests
import re
import json

def inspect_page():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    url = 'https://www.investing.com/central-banks/fed-rate-monitor'
    r = requests.get(url, headers=headers, impersonate='chrome120', timeout=15)
    
    # Find all script tags containing JSON or numbers
    scripts = re.findall(r'<script.*?>([\s\S]*?)</script>', r.text)
    print(f"Total scripts: {len(scripts)}")
    for s in scripts:
        if any(k in s.lower() for k in ["fedwatch", "probability", "targetrate", "ease"]):
            print("--- Matching Script ---")
            print(s[:500])

if __name__ == '__main__':
    inspect_page()
