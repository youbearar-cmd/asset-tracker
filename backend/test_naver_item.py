import requests
import re

def get_kr_info(code):
    url = f"https://finance.naver.com/item/main.naver?code={code}"
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
    r.encoding = 'euc-kr'
    html = r.text
    # Name pattern
    name_match = re.search(r'<h2><a href=".*?">(.*?)</a></h2>', html)
    # Price pattern
    price_match = re.search(r'<p class="no_today">.*?<span class="blind">(.*?)</span>', html, re.DOTALL)
    
    name = name_match.group(1) if name_match else "Unknown"
    price = price_match.group(1).replace(',', '') if price_match else None
    return name, price

print(f"SOL 국제금 (486600): {get_kr_info('486600')}")
print(f"SOL 금현물 (461580): {get_kr_info('461580')}")
print(f"삼성전자 (005930): {get_kr_info('005930')}")
