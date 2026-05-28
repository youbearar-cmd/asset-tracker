import requests

query = "삼성전자"
url = f"https://search.naver.com/search.naver?query={query}"
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}, timeout=5)
with open("naver_search.html", "w", encoding="utf-8") as f:
    f.write(r.text)
print("Saved naver_search.html")
