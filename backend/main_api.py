import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
import asset_db
import price_service

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AssetIn(BaseModel):
    name: str
    symbol: str
    type: str
    quantity: float

class AssetOut(BaseModel):
    id: int
    name: str
    symbol: str
    type: str
    quantity: float
    current_price: float
    value_krw: int

@app.on_event("startup")
def startup_event():
    import os
    db_url = os.environ.get("DATABASE_URL", "NOT SET")
    print(f"DATABASE_URL starts with: {db_url[:40] if db_url != 'NOT SET' else 'NOT SET'}")
    try:
        asset_db.init_db()
        print("DB init successful")
    except Exception as e:
        print(f"DB init FAILED (app will still start): {e}")

@app.get("/api/search")
def search(q: str):
    print(f"API Search Request: {q}")
    results = price_service.search_symbol(q)
    print(f"API Search Results count: {len(results)}")
    return results

@app.get("/api/assets")
async def get_assets():
    print(f"API Fetching Assets...")
    assets = asset_db.get_all_assets()
    evaluated, total_krw, rate = await price_service.evaluate_assets(assets)
    
    # Calculate distribution
    distribution = {
        "원화": 0,
        "외화": 0,
        "주식": 0,
        "비트코인": 0,
        "금": 0
    }
    
    for a in evaluated:
        symbol = a['symbol'].upper()
        asset_type = a.get('type', '').upper()
        asset_name = a.get('name', '').upper()
        val = a['value_krw']
        
        if symbol == "KRW" or asset_type == "CASH":
            distribution["원화"] += val
        elif symbol == "USD" or ("USD" in symbol and asset_type == "CASH"):
            distribution["외화"] += val
        elif asset_type in ["CRYPTOCURRENCY", "COIN"]:
            distribution["비트코인"] += val
        elif "GC=F" in symbol or asset_type == "GOLD" or "금" in asset_name or "GOLD" in asset_name:
            distribution["금"] += val
        else:
            # Default to stocks for others
            distribution["주식"] += val

    # Save today's history automatically with details
    if total_krw > 0:
        asset_db.save_daily_history(total_krw, evaluated)
        
    from datetime import datetime
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    return {
        "assets": evaluated,
        "total_value_krw": total_krw,
        "exchange_rate": rate,
        "distribution": distribution,
        "last_updated": last_updated
    }

@app.get("/api/history")
def get_history():
    return asset_db.get_asset_history()

@app.get("/api/history/{date}")
def get_history_details(date: str):
    details = asset_db.get_asset_history_details(date)
    if not details:
        raise HTTPException(status_code=404, detail="No details found for this date")
    return details

@app.post("/api/assets")
def add_asset(asset: AssetIn):
    success = asset_db.add_asset(asset.name, asset.symbol, asset.type, asset.quantity)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add asset")
    return {"message": "Asset added successfully"}

@app.put("/api/assets/{asset_id}")
def update_asset(asset_id: int, quantity: float):
    asset_db.update_asset_quantity(asset_id, quantity)
    return {"message": "Asset updated successfully"}

@app.delete("/api/assets/{asset_id}")
def delete_asset(asset_id: int):
    asset_db.delete_asset(asset_id)
    return {"message": "Asset deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
