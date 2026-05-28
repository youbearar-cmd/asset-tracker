import requests
import urllib.parse

def test_endpoints(query):
    encoded_query = urllib.parse.quote(query)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://finance.yahoo.com/'
    }
    
    endpoints = [
        f"https://query1.finance.yahoo.com/v1/finance/search?q={encoded_query}&lang=ko-KR&region=KR",
        f"https://query2.finance.yahoo.com/v1/finance/search?q={encoded_query}&quotesCount=10",
        f"https://finance.yahoo.com/_finance_doubledown/api/resource/searchassist;searchTerm={encoded_query}"
    ]
    
    for url in endpoints:
        try:
            print(f"Testing URL: {url}")
            r = requests.get(url, headers=headers, timeout=5)
            print(f"Status: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                quotes = data.get('quotes', data.get('data', {}).get('items', []))
                print(f"Found {len(quotes)} results")
                if quotes:
                    print(f"First result: {quotes[0].get('symbol')} - {quotes[0].get('shortname')}")
                    return True
        except Exception as e:
            print(f"Error: {e}")
    return False

if __name__ == "__main__":
    test_endpoints("삼성전자")
    print("-" * 20)
    test_endpoints("TIGER 일본니케이")
