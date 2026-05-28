import requests
import re

def get_kr_info_alphanumeric(code):
    url = f"https://finance.naver.com/item/main.naver?code={code}"
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
    r.encoding = 'euc-kr'
    html = r.text
    
    # Name pattern
    name_match = re.search(r'<h2><a href=".*?">(.*?)</a></h2>', html)
    if not name_match:
        name_match = re.search(r'<title>(.*?) : 네이버 페이 증권</title>', html)
    
    # Price pattern
    price_match = re.search(r'<p class="no_today">.*?<span class="blind">(.*?)</span>', html, re.DOTALL)
    
    name = name_match.group(1).strip() if name_match else "Unknown"
    price = price_match.group(1).replace(',', '') if price_match else None
    return name, price

code = "0066W0"
print(f"Info for {code}: {get_kr_info_alphanumeric(code)}")
