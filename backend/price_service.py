import yfinance as yf
import pandas as pd
import requests
import re
import asyncio

def get_price_from_naver(code):
    """
    Fetches the current price from Naver Finance as a fallback.
    """
    try:
        url = f"https://finance.naver.com/item/main.naver?code={code}"
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        # Naver has switched to UTF-8
        html = r.text
        # Look for the blind span within no_today p tag
        price_match = re.search(r'<p class="no_today">.*?<span class="blind">(.*?)</span>', html, re.DOTALL)
        if price_match:
            return float(price_match.group(1).replace(',', ''))
        return None
    except Exception as e:
        print(f"Naver price fetch error for {code}: {e}")
        return None

def get_current_price(symbol):
    """
    Fetches the current price of a given symbol using yfinance, with Naver fallback for KR.
    """
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period='1d')
        if not data.empty:
            return data['Close'].iloc[-1]
        
        # Fallback for Korean stocks if Yahoo fails
        if symbol.endswith('.KS') or symbol.endswith('.KQ'):
            code = symbol.split('.')[0]
            return get_price_from_naver(code)
            
        return None
    except Exception as e:
        print(f"Error fetching price for {symbol}: {e}")
        # Final fallback check for KR
        if symbol.endswith('.KS') or symbol.endswith('.KQ'):
            code = symbol.split('.')[0]
            return get_price_from_naver(code)
        return None

def get_exchange_rate_usdkrw():
    """
    Fetches the latest USD/KRW exchange rate.
    Tries yfinance first, then Frankfurter API as fallback.
    """
    # 1. Try yfinance
    try:
        ticker = yf.Ticker("USDKRW=X")
        data = ticker.history(period='1d')
        if not data.empty:
            rate = float(data['Close'].iloc[-1])
            if rate > 100:  # sanity check
                print(f"Exchange rate from yfinance: {rate}")
                return rate
    except Exception as e:
        print(f"yfinance exchange rate failed: {e}")

    # 2. Try Frankfurter API (free, no key required)
    try:
        r = requests.get('https://api.frankfurter.app/latest?from=USD&to=KRW', timeout=5)
        if r.status_code == 200:
            rate = float(r.json()['rates']['KRW'])
            print(f"Exchange rate from Frankfurter: {rate}")
            return rate
    except Exception as e:
        print(f"Frankfurter exchange rate failed: {e}")

    print("Using fallback exchange rate: 1380.0")
    return 1380.0

def search_symbol(query):
    """
    Robust search handling Korean (via Naver/Upbit) and English (via Yahoo).
    """
    print(f"Searching for: {query}")
    results = []

    # 0. Check if query is a 6-character ticker code (numeric or alphanumeric)
    if len(query) == 6:
        code = query.upper()
        try:
            url = f"https://finance.naver.com/item/main.naver?code={code}"
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
            # Naver Finance now uses UTF-8
            html = r.text
            # Look for the title which contains the asset name
            title_match = re.search(r'<title>(.*?) : 네이버 페이 증권</title>', html)
            if title_match:
                name = title_match.group(1).strip()
                if name and name != "Npay 증권":
                    results.append({
                        "symbol": f"{code}.KS",
                        "name": name,
                        "type": "EQUITY/ETF",
                        "exchange": "KRX"
                    })
        except:
            pass

    # 0.5. Explicit SOL/ACE specific matches if search fails
    if "SOL" in query.upper() and "국제금" in query:
        results.append({"symbol": "0066W0.KS", "name": "SOL 국제금", "type": "EQUITY/ETF", "exchange": "KRX"})
    elif "SOL" in query.upper() and "금" in query:
        results.append({"symbol": "461580.KS", "name": "SOL 금현물(H)", "type": "EQUITY/ETF", "exchange": "KRX"})

    # 1. Explicit KRW/USD/Gold Cash match
    if query in ["원화", "현금", "KRW", "krw", "cash", "Cash"]:
        results.append({"symbol": "KRW", "name": "원화 현금", "type": "Cash", "exchange": "Internal"})
    elif query in ["달러", "USD", "usd", "dollar", "Dollar"]:
        results.append({"symbol": "USD", "name": "달러 현금", "type": "Cash", "exchange": "Internal"})
    elif query in ["금", "gold", "Gold", "GOLD"]:
        results.append({"symbol": "GC=F", "name": "금 (Gold Futures)", "type": "Gold", "exchange": "COMEX"})
    
    # 2. Search Upbit (Crypto)
    try:
        r = requests.get('https://api.upbit.com/v1/market/all', timeout=5)
        if r.status_code == 200:
            markets = r.json()
            for m in markets:
                if query in m['korean_name'] or query.upper() in m['english_name'].upper() or query.upper() in m['market']:
                    if m['market'].startswith('KRW-'):
                        results.append({
                            "symbol": f"{m['market'].split('-')[1]}-USD",
                            "name": m['korean_name'],
                            "type": "CRYPTOCURRENCY",
                            "exchange": "Upbit/Yahoo"
                        })
    except Exception as e:
        print(f"Upbit search error: {e}")

    # 3. Search Naver for Korean Stock/ETF Tickers
    etf_brands = ["TIGER", "KODEX", "SOL", "ACE", "RISE", "KBSTAR", "HANARO", "KOSEF"]
    if any(ord(c) > 127 for c in query) or any(brand in query.upper() for brand in etf_brands):
        try:
            def get_codes_from_naver(q):
                """
                Scrapes search.naver.com to find potential 6-digit stock codes.
                """
                url = f"https://search.naver.com/search.naver?query={q}"
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                r = requests.get(url, headers=headers, timeout=5)
                html = r.text
                # Multiple patterns to find codes
                c1 = re.findall(r'code=(\d{6})', html)
                c2 = re.findall(r'data-code="(\d{6})"', html)
                c3 = re.findall(r'ticker\s*:\s*"(\d{6})"', html)
                c4 = re.findall(r'>(\d{6})</a>', html)
                return list(dict.fromkeys(c1 + c2 + c3 + c4))

            search_queries = [query]
            if len(query) <= 5 or any(brand in query.upper() for brand in etf_brands):
                search_queries.append(query + " 주식")
                search_queries.append(query + " ETF")

            all_codes = []
            for sq in search_queries:
                all_codes.extend(get_codes_from_naver(sq))
            
            codes = list(dict.fromkeys(all_codes))
            
            for code in codes:
                if not code.isdigit() or len(code) != 6: continue
                # Skip some known irrelevant codes if any
                if code == "037403": continue 
                
                try:
                    if any(r['symbol'].startswith(code) for r in results): continue
                    url = f"https://finance.naver.com/item/main.naver?code={code}"
                    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
                    # Naver Finance now uses UTF-8
                    html = r.text
                    # More robust title parsing
                    title_match = re.search(r'<title>(.*?) : 네이버 페이 증권</title>', html)
                    if not title_match:
                         title_match = re.search(r'<title>(.*?)</title>', html)
                         
                    if title_match:
                        real_name = title_match.group(1).split(':')[0].strip()
                        if real_name and real_name != "Npay 증권":
                            results.append({
                                "symbol": f"{code}.KS",
                                "name": real_name,
                                "type": "EQUITY/ETF",
                                "exchange": "KRX"
                            })
                    if len(results) >= 15: break
                except:
                    continue
        except Exception as e:
            print(f"Naver scraping search error: {e}")

    # 4. Search Yahoo
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        url = "https://query1.finance.yahoo.com/v1/finance/search"
        response = requests.get(url, params={'q': query, 'quotesCount': 10}, headers=headers, timeout=5)
        if response.status_code == 200:
            quotes = response.json().get('quotes', [])
            for quote in quotes:
                results.append({
                    "symbol": quote.get("symbol"),
                    "name": quote.get("shortname") or quote.get("longname"),
                    "type": quote.get("quoteType"),
                    "exchange": quote.get("exchange")
                })
    except Exception as e:
        print(f"Yahoo search error: {e}")
            
    seen = set()
    unique_results = []
    for r in results:
        if r['symbol'] not in seen:
            unique_results.append(r)
            seen.add(r['symbol'])
            
    print(f"Found {len(unique_results)} results")
    return unique_results[:10]

async def evaluate_assets(assets):
    """
    Takes a list of asset dicts and adds current price and evaluation in KRW.
    Uses asyncio for parallel price fetching.
    """
    exchange_rate = await asyncio.to_thread(get_exchange_rate_usdkrw)
    
    async def evaluate_single_asset(asset):
        symbol = asset['symbol']
        quantity = asset['quantity']
        
        if asset.get('type') == 'Cash' or symbol.upper() in ["KRW", "현금", "원화", "USD", "달러"]:
            if symbol.upper() in ["USD", "달러"]:
                price = exchange_rate
                value_krw = quantity * exchange_rate
            else:
                price = 1
                value_krw = quantity
                
            return {**asset, 'current_price': price, 'value_krw': round(value_krw)}

        price = await asyncio.to_thread(get_current_price, symbol)
        
        if price is None:
            return {**asset, 'current_price': 0, 'value_krw': 0}
            
        is_krw = symbol.endswith(".KS") or symbol.endswith(".KQ") or "KRW" in symbol
        
        if is_krw:
            value_krw = quantity * price
        else:
            value_krw = quantity * price * exchange_rate
            
        return {**asset, 'current_price': price, 'value_krw': round(value_krw)}

    # Fetch all prices in parallel
    evaluated_assets = await asyncio.gather(*(evaluate_single_asset(a) for a in assets))
    
    total_value_krw = sum(a['value_krw'] for a in evaluated_assets)
        
    return list(evaluated_assets), round(total_value_krw), exchange_rate

if __name__ == "__main__":
    # Test block
    async def test():
        test_assets = [
            {'symbol': 'AAPL', 'quantity': 10},
            {'symbol': 'BTC-USD', 'quantity': 0.1},
            {'symbol': '005930.KS', 'quantity': 5}
        ]
        evaluated, total, rate = await evaluate_assets(test_assets)
        print(f"Total Portfolio Value: {total:,} KRW (Exchange Rate: {rate})")
        for a in evaluated:
            print(f"{a['symbol']}: {a['value_krw']:,} KRW")
    
    asyncio.run(test())
