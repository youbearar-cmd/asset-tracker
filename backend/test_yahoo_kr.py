import requests

query = "sol 금"
url = "https://query1.finance.yahoo.com/v1/finance/search"
params = {
    'q': query,
    'quotesCount': 10,
    'lang': 'ko-KR',
    'region': 'KR'
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
response = requests.get(url, params=params, headers=headers, timeout=5)
print(response.json())
