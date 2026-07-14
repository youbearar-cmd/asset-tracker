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
    category: Optional[str] = None

class CategoryIn(BaseModel):
    category: Optional[str] = None

STOCK_CATEGORIES = ["한국주식", "미국주식", "미국채권"]

# Common US-listed bond ETF tickers, used for auto-classification.
BOND_TICKERS = {
    "TLT", "IEF", "SHY", "SHV", "BND", "AGG", "LQD", "HYG", "TIP", "TIPS",
    "SCHZ", "GOVT", "BIL", "IEI", "EDV", "VGIT", "VGLT", "VCIT", "VCLT",
    "MUB", "JNK", "SPTL", "SPTS", "USIG", "TLH", "BNDX", "BSV", "BIV", "BLV",
    "TMF", "TMV", "TBT", "TBF", "PST", "SPAB", "FBND", "TFLO", "FLOT",
    "MINT", "ICSH", "NEAR", "SGOV", "BILS",
}

def classify_stock_category(symbol: str, manual_category: Optional[str] = None) -> str:
    """Resolves a non-cash/crypto/gold asset into 한국주식/미국주식/미국채권.
    Manual category (set by the user) always wins over auto-detection.
    """
    if manual_category in STOCK_CATEGORIES:
        return manual_category

    symbol_up = symbol.upper()
    if symbol_up.endswith(".KS") or symbol_up.endswith(".KQ"):
        return "한국주식"

    base_symbol = symbol_up.split(".")[0]
    if base_symbol in BOND_TICKERS:
        return "미국채권"

    return "미국주식"

class CashDetailIn(BaseModel):
    currency: str = 'KRW'
    label: str
    amount: float
    note: str = ''

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
    try:
        asset_db.init_db()
    except Exception as e:
        print(f"DB init failed: {e}")

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
        "한국주식": 0,
        "미국주식": 0,
        "미국채권": 0,
        "비트코인": 0,
        "금": 0
    }

    for a in evaluated:
        symbol = a['symbol'].upper()
        asset_type = a.get('type', '').upper()
        asset_name = a.get('name', '').upper()
        val = a['value_krw']

        if symbol == "USD":
            category = "외화"
        elif symbol == "KRW" or asset_type == "CASH":
            category = "원화"
        elif asset_type in ["CRYPTOCURRENCY", "COIN"]:
            category = "비트코인"
        elif "GC=F" in symbol or asset_type == "GOLD" or "금" in asset_name or "GOLD" in asset_name:
            category = "금"
        else:
            category = classify_stock_category(a['symbol'], a.get('category'))

        a['display_category'] = category
        distribution[category] += val

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
    success = asset_db.add_asset(asset.name, asset.symbol, asset.type, asset.quantity, asset.category)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add asset")
    return {"message": "Asset added successfully"}

@app.put("/api/assets/{asset_id}")
def update_asset(asset_id: int, quantity: float):
    asset_db.update_asset_quantity(asset_id, quantity)
    return {"message": "Asset updated successfully"}

@app.put("/api/assets/{asset_id}/category")
def update_asset_category(asset_id: int, body: CategoryIn):
    if body.category is not None and body.category not in STOCK_CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid category")
    asset_db.update_asset_category(asset_id, body.category)
    return {"message": "Category updated successfully"}

@app.delete("/api/assets/{asset_id}")
def delete_asset(asset_id: int):
    asset_db.delete_asset(asset_id)
    return {"message": "Asset deleted successfully"}

@app.get("/api/cash-details")
def get_cash_details(currency: Optional[str] = None):
    return asset_db.get_cash_details(currency)

@app.post("/api/cash-details")
def add_cash_detail(detail: CashDetailIn):
    asset_db.add_cash_detail(detail.currency, detail.label, detail.amount, detail.note)
    return {"message": "Cash detail added successfully"}

@app.put("/api/cash-details/{detail_id}")
def update_cash_detail(detail_id: int, detail: CashDetailIn):
    asset_db.update_cash_detail(detail_id, detail.label, detail.amount, detail.note)
    return {"message": "Cash detail updated successfully"}

@app.delete("/api/cash-details/{detail_id}")
def delete_cash_detail(detail_id: int):
    asset_db.delete_cash_detail(detail_id)
    return {"message": "Cash detail deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
