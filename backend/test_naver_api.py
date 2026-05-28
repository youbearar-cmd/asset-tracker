import requests

query = "sol 금"
url = f"https://m.stock.naver.com/api/search/getSearchList.nhn?keyword={query}"
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
print(r.text)
