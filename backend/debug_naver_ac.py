import requests
import json
import urllib.parse

def test_naver_ac_api(query, enc='utf-8'):
    print(f"Testing Naver AC API with query: {query} (Encoding: {enc})")
    
    # Try different encoding settings
    url = f"https://ac.finance.naver.com/ac?q={urllib.parse.quote(query, encoding=enc)}&q_enc={enc}&st=111&frm=stock&r_format=json&r_enc={enc}&r_unicode=1&t_koreng=1"
    
    try:
        r = requests.get(url, timeout=5)
        print(f"Status: {r.status_code}")
        data = r.json()
        print(f"Response: {json.dumps(data, ensure_ascii=False)}")
        
        items = data.get('items', [])
        if items and items[0]:
            print(f"Found {len(items[0])} items in first group.")
            for item in items[0]:
                print(f" - Name: {item[0][0]}, Code: {item[1][0]}")
        else:
            print("No items found in response.")
            
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 50)

if __name__ == "__main__":
    test_naver_ac_api("삼성전자", "utf-8")
    test_naver_ac_api("삼성전자", "euc-kr")
    test_naver_ac_api("SK하이닉스", "utf-8")
