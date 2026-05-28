import price_service
import requests
import re

def manual_check(code):
    print(f"Manual check for {code}...")
    try:
        url = f"https://finance.naver.com/item/main.naver?code={code}"
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        r.encoding = 'euc-kr'
        print(f"Status: {r.status_code}")
        # print(f"HTML snippet: {r.text[:500]}")
        title_match = re.search(r'<title>(.*?) : 네이버 페이 증권</title>', r.text)
        if title_match:
            print(f"Title found: {title_match.group(1)}")
        else:
            print("Title NOT found")
            # Try a broader title search
            t2 = re.search(r'<title>(.*?)</title>', r.text)
            if t2:
                print(f"Broad Title: {t2.group(1)}")
    except Exception as e:
        print(f"Error: {e}")

codes = ["486600", "461580", "005930"]
for code in codes:
    manual_check(code)
    print("-" * 10)
    results = price_service.search_symbol(code)
    print(f"Results for '{code}': {results}")
    print("=" * 20)
