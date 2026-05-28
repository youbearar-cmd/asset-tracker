import requests
import re

query = "sol 국제금"
url = f"https://search.naver.com/search.naver?query={query}+주가"
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
html = r.text
codes = re.findall(r'code=(\d{6})', html)
print(f"Codes for '{query} 주가': {codes}")
