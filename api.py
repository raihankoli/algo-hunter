# api.py
from fastapi import FastAPI, HTTPException, Header
import json
import os

app = FastAPI(title="Algo Hunter Simple API")

# optional simple API key check (recommended)
API_KEY = os.environ.get("ALGO_API_KEY", "change_me_very_secret")

@app.get("/health")
def health():
    return {"status":"ok"}

@app.get("/top10")
def get_top(x_api_key: str = Header(None)):
    # API key check (if you set one on server)
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # ensure file exists
    path = "enriched_coins.json"
    if not os.path.exists(path):
        raise HTTPException(status_code=500, detail=f"{path} not found in repo")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    scored = []
    for c in data:
        mc = c.get("quote", {}).get("USD", {}).get("market_cap", 0) or 0
        binance = 1 if c.get("binance_pair") else 0
        coinbase = 1 if c.get("coinbase_pair") else 0
        # score formula (adjust later)
        score = (binance * 150) + (coinbase * 90) + (0 if mc == 0 else (mc**0.5))
        c["_score"] = score
        scored.append(c)

    ranked = sorted(scored, key=lambda x: x["_score"], reverse=True)[:10]
    # return minimal fields to keep response small
    out = []
    for i, r in enumerate(ranked, start=1):
        out.append({
            "rank": i,
            "id": r.get("id"),
            "name": r.get("name"),
            "symbol": r.get("symbol"),
            "score": r.get("_score"),
            "binance_pair": r.get("binance_pair"),
            "coinbase_pair": r.get("coinbase_pair"),
            "price": r.get("quote", {}).get("USD", {}).get("price")
        })
    return {"top10": out}