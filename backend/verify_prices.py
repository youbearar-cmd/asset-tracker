import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'asset-tracker', 'backend'))
import price_service

async def check_realtime():
    print("--- Real-time Price Verification ---")
    test_assets = [
        {'symbol': '005930.KS', 'quantity': 1, 'name': '삼성전자'},
        {'symbol': 'AAPL', 'quantity': 1, 'name': 'Apple'},
        {'symbol': 'USDKRW=X', 'quantity': 1, 'name': 'USD/KRW'}
    ]
    
    evaluated, total, rate = await price_service.evaluate_assets(test_assets)
    
    for a in evaluated:
        print(f"Asset: {a['name']} ({a['symbol']})")
        print(f"  Price: {a['current_price']:,}")
        print(f"  Value (KRW): {a['value_krw']:,}")
        print("-" * 30)
    
    print(f"Current USD/KRW Rate: {rate}")

if __name__ == "__main__":
    asyncio.run(check_realtime())
