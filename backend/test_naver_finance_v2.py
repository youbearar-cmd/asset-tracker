import requests
import re

query = "sol 금"
url = f"https://finance.naver.com/search/searchList.naver?query={query}"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://finance.naver.com/'
}
r = requests.get(url, headers=headers, timeout=5)
print(f"Status: {r.status_code}")
# Naver Finance search uses EUC-KR often.
r.encoding = 'euc-kr'
html = r.text
codes = re.findall(r'code=(\d{6})', html)
print(f"Codes: {codes}")
if codes:
    # Try to find the name
    names = re.findall(r'<a href="/item/main\.naver\?code=\d{6}">(.*?)</a>', html)
    print(f"Names: {names}")
