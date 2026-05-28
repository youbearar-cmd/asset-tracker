import requests
import urllib.parse
import re

query = "삼성전자"
encoded_query = urllib.parse.quote(query, encoding='euc-kr')
url = f"https://finance.naver.com/search/searchList.naver?query={encoded_query}"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://finance.naver.com/'
}
r = requests.get(url, headers=headers, timeout=5)
# Naver Finance search uses EUC-KR
html = r.content.decode('euc-kr', errors='ignore')
codes = re.findall(r'code=(\d{6})', html)
print(f"Codes: {codes}")
if codes:
    # Find names
    names = re.findall(r'target="_top">(.*?)</a>', html)
    print(f"Names: {names}")
