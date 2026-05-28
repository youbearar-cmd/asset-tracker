import requests

query = "sol 금"
url = f"https://m.stock.naver.com/api/stock/search?keyword={query}&pageSize=20&page=1"
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
print(r.json())
