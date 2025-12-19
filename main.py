# main.py
import json
import argparse
import os
from typing import List, Dict, Any, Optional

def load_json_file(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"{path} does not contain a JSON list")
    return data


def extract_asset_info(item: Dict[str, Any]) -> Dict[str, Any]:
    usd = item.get("quote", {}).get("USD", {}) if isinstance(item.get("quote"), dict) else {}
    return {
        "id": item.get("id"),
        "name": item.get("name"),
        "symbol": (item.get("symbol") or "").upper(),
        "price": usd.get("price"),
        "market_cap": usd.get("market_cap"),
    }


def get_assets_data() -> List[Dict[str, Any]]:
    if os.path.exists("enriched_coins.json"):
        data_file = "enriched_coins.json"
    else:
        data_file = "coins.json"
    return load_json_file(data_file)


def get_preview_assets(show: int = 5) -> List[Dict[str, Any]]:
    assets = get_assets_data()
    return [extract_asset_info(a) for a in assets[:show]]


def cli_main():
    parser = argparse.ArgumentParser(description="Algo Hunter - coins preview")
    parser.add_argument("--show", "-s", type=int, default=5, help="How many items to show")
    args = parser.parse_args()

    try:
        assets = get_assets_data()
    except Exception as e:
        raise SystemExit(f"❌ Error loading data: {e}")

    print("🚀 ALGO HUNTER ENGINE STARTED")
    print(f"🔍 Total assets loaded: {len(assets)}\n")

    for i, a in enumerate(assets[:args.show], start=1):
        info = extract_asset_info(a)
        print(f"{i}. {info['symbol']} — {info['name']}")
        print(f"   id: {info['id']}")
        print(f"   price: {info['price']}")
        print(f"   market_cap: {info['market_cap']}\n")

    print("🎯 Algo Hunter run complete!")


# ---------------- FASTAPI (PRODUCTION) ----------------

from fastapi import FastAPI, Header, HTTPException, Query
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")  # Render env var

app = FastAPI(title="Algo Hunter API")
@app.get("/")
def root():
    return {
        "service": "algo-hunter",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
}

def check_api_key(x_api_key: Optional[str]):
    if API_KEY:
        if not x_api_key or x_api_key != API_KEY:
            raise HTTPException(status_code=401, detail="Invalid or missing API key")


class PreviewResponse(BaseModel):
    total: int
    preview: List[Dict[str, Any]]


@app.get("/health")
def health():
    return {"status": "ok", "service": "algo-hunter"}


@app.get("/preview", response_model=PreviewResponse)
def preview(
    show: int = Query(5, ge=1, le=100),
    x_api_key: Optional[str] = Header(None),
):
    check_api_key(x_api_key)
    assets = get_assets_data()
    return {
        "total": len(assets),
        "preview": get_preview_assets(show),
    }


@app.get("/top10")
def top10(x_api_key: Optional[str] = Header(None)):
    check_api_key(x_api_key)
    assets = get_assets_data()

    scored = []
    for c in assets:
        mc = c.get("quote", {}).get("USD", {}).get("market_cap", 0) or 0
        binance = 1 if c.get("binance_pair") else 0
        coinbase = 1 if c.get("coinbase_pair") else 0
        score = (binance * 150) + (coinbase * 90) + (0 if mc == 0 else (mc ** 0.5))
        scored.append((score, c))

    ranked = sorted(scored, key=lambda x: x[0], reverse=True)[:10]

    out = []
    for i, (score, r) in enumerate(ranked, start=1):
        out.append({
            "rank": i,
            "id": r.get("id"),
            "name": r.get("name"),
            "symbol": (r.get("symbol") or "").upper(),
            "score": score,
            "binance_pair": r.get("binance_pair"),
            "coinbase_pair": r.get("coinbase_pair"),
            "price": r.get("quote", {}).get("USD", {}).get("price"),
        })

    return {"top10": out}


# ---------------- ENTRY POINT ----------------

if __name__ == "__main__":
    cli_main()
