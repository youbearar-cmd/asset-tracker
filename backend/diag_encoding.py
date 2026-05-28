import requests
import re

def diagnostic():
    code = "005930" # 삼성전자
    url = f"https://finance.naver.com/item/main.naver?code={code}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    r = requests.get(url, headers=headers, timeout=5)
    raw_content = r.content
    
    print(f"--- Diagnostic for {code} ---")
    print(f"Content Length: {len(raw_content)}")
    
    # Try decoding with different codecs
    codecs = ['euc-kr', 'cp949', 'utf-8']
    for c in codecs:
        try:
            decoded = raw_content.decode(c, errors='replace')
            title_match = re.search(r'<title>(.*?)</title>', decoded)
            title = title_match.group(1) if title_match else "No title found"
            print(f"Codec {c}: {title[:50]}")
        except Exception as e:
            print(f"Codec {c} failed: {e}")

    # Check the actual bytes of a known garbled string if possible
    # But let's just see what we get here.

if __name__ == "__main__":
    diagnostic()
