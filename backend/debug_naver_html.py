import requests

query = "sol 금"
url = f"https://search.naver.com/search.naver?query={query}"
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
print(r.text[:5000]) # Print first 5000 chars
