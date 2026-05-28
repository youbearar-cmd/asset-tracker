import requests

def manual_search(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=10&newsCount=0"
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        return data.get('quotes', [])
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    q = "삼성전자"
    results = manual_search(q)
    print(f"Results for {q}:")
    for r in results:
        print(r)
