import requests

query = "sol 금"
url = f"https://suggest-stock.naver.com/suggest?q={query}&c=ko&t=all"
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
print(r.json())
