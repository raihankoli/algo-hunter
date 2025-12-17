# leaderboard.py
import json
import csv
from pathlib import Path

IN = Path("enriched_coins.json")
OUT = Path("top10.csv")

if not IN.exists():
    raise SystemExit("enriched_coins.json not found.")

with IN.open("r", encoding="utf-8") as f:
    coins = json.load(f)

# Sort by market cap (if present), descending. Fallback 0.
def mcap(x):
    try:
        return float(x.get("quote", {}).get("USD", {}).get("market_cap") or 0)
    except Exception:
        return 0

sorted_coins = sorted(coins, key=mcap, reverse=True)

top = sorted_coins[:10]

# fields to write
fields = ["rank", "id", "name", "symbol", "market_cap", "price", "binance_pair", "coinbase_pair"]

with OUT.open("w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writeheader()
    for i, c in enumerate(top, 1):
        row = {
            "rank": i,
            "id": c.get("id"),
            "name": c.get("name"),
            "symbol": c.get("symbol"),
            "market_cap": c.get("quote", {}).get("USD", {}).get("market_cap"),
            "price": c.get("quote", {}).get("USD", {}).get("price"),
            "binance_pair": c.get("binance_pair"),
            "coinbase_pair": c.get("coinbase_pair"),
        }
        writer.writerow(row)

print(f"Top {len(top)} written to {OUT}")