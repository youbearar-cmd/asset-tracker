import requests
import re

query = "sol 금"
url = f"https://finance.naver.com/search/searchList.naver?query={query}"
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
html = r.text
codes = re.findall(r'code=(\d{6})', html)
print(f"Codes from Naver Finance: {codes}")
