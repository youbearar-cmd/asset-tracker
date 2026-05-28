import requests
import json

def test_search(query):
    url = f"http://localhost:8000/api/search?q={query}"
    try:
        response = requests.get(url, timeout=5)
        print(f"Search Query: {query}")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            results = response.json()
            print(f"Results Count: {len(results)}")
            if results:
                print(f"First Result: {results[0]}")
            else:
                print("No results found.")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    # Test with common tickers
    test_search("AAPL")
    test_search("삼성전자")
    test_search("005930")
