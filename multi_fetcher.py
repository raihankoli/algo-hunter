#!/usr/bin/env python3
"""
Final multi_fetcher.py — resumable full-market fetch + auto-batch exchange enrichment.

Usage examples:
  # 1) Fetch whole market (resume-safe)
  python multi_fetcher.py --fetch --limit 5000 --delay 1

  # 2) Auto-enrich (batch probe) using existing coins.json
  python multi_fetcher.py --auto-enrich --batch-size 300 --exchange-delay 0.12

  # 3) Do both in sequence:
  python multi_fetcher.py --fetch --limit 5000 --delay 1 --auto-enrich --batch-size 300
"""
import os
import time
import json
import argparse
from typing import List, Dict, Optional
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("CMC_API_KEY")
if not API_KEY:
    raise SystemExit("ERROR: CMC_API_KEY not found in .env (create .env with CMC_API_KEY=...)")

CMC_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
BINANCE_TICKER = "https://api.binance.com/api/v3/ticker/price?symbol={}"
COINBASE_SPOT = "https://api.coinbase.com/v2/prices/{}-USD/spot"
HEADERS = {"Accepts": "application/json", "X-CMC_PRO_API_KEY": API_KEY}


def fetch_all_coins(limit: int = 5000, start: int = 1, delay_seconds: float = 1.0, out_file: str = "coins.json"):
    all_data: List[Dict] = []
    current_start = start

    # resume if exists
    if os.path.exists(out_file):
        try:
            with open(out_file, "r", encoding="utf-8") as f:
                existing = json.load(f)
            if isinstance(existing, list):
                all_data = existing
                current_start = 1 + len(all_data)
                print(f"[resume] loaded {len(all_data)} records; next start={current_start}")
        except Exception:
            print("Warning: couldn't load existing coins.json; starting fresh.")

    session = requests.Session()
    session.headers.update(HEADERS)

    while True:
        params = {"start": current_start, "limit": limit, "convert": "USD"}
        print(f"Fetching (start={current_start}, limit={limit}) ...")
        retry = 0
        while True:
            try:
                r = session.get(CMC_URL, params=params, timeout=20)
                if r.status_code == 429:
                    backoff = min(60, 2 ** retry)
                    print(f"Rate limited (429). Backing off {backoff}s (retry {retry+1})...")
                    time.sleep(backoff)
                    retry += 1
                    if retry > 6:
                        raise RuntimeError("Max retries for 429")
                    continue
                r.raise_for_status()
                data = r.json().get("data", [])
                break
            except requests.RequestException as e:
                retry += 1
                backoff = min(60, 2 ** retry)
                print(f"Request error: {e}. Backing off {backoff}s (retry {retry})...")
                time.sleep(backoff)
                if retry > 6:
                    print("Max retries exceeded. Returning what we have.")
                    return all_data

        if not data:
            print("No more data from CMC. Finished fetching.")
            break

        all_data.extend(data)
        print(f"Added {len(data)} items -> total {len(all_data)}")

        # save progress after each page
        try:
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            print(f"Saved progress: {len(all_data)} -> {out_file}")
        except Exception as e:
            print("Warning: failed to save progress:", e)

        if len(data) < limit:
            print("Last page fetched (returned less than limit).")
            break

        current_start += limit
        time.sleep(delay_seconds)

    print(f"Fetch complete: {len(all_data)} records saved to {out_file}")
    return all_data


def probe_binance(symbol: str, session: Optional[requests.Session] = None, timeout: float = 3.0) -> Optional[str]:
    if not symbol:
        return None
    s = symbol.upper()
    candidates = [f"{s}USDT", f"{s}BUSD", f"{s}BTC"]
    if session is None:
        session = requests.Session()
    for c in candidates:
        try:
            r = session.get(BINANCE_TICKER.format(c), timeout=timeout)
            if r.status_code == 200:
                return c
        except requests.RequestException:
            continue
    return None


def probe_coinbase(symbol: str, session: Optional[requests.Session] = None, timeout: float = 4.0) -> Optional[str]:
    if not symbol:
        return None
    s = symbol.upper()
    url = COINBASE_SPOT.format(s)
    if session is None:
        session = requests.Session()
    try:
        r = session.get(url, timeout=timeout)
        if r.status_code == 200:
            return f"{s}-USD"
    except requests.RequestException:
        pass
    return None


def enrich_batch(coins_slice: List[Dict], exchange_delay: float = 0.12):
    out = []
    session = requests.Session()
    for c in coins_slice:
        sym = (c.get("symbol") or "").upper()
        bin_pair = None
        cb_pair = None
        if sym:
            try:
                bin_pair = probe_binance(sym, session=session)
            except Exception:
                bin_pair = None
            time.sleep(exchange_delay)
            try:
                cb_pair = probe_coinbase(sym, session=session)
            except Exception:
                cb_pair = None
        c2 = dict(c)
        c2["binance_pair"] = bin_pair
        c2["coinbase_pair"] = cb_pair
        out.append(c2)
    return out


def auto_enrich_all(coins_file: str = "coins.json", enriched_file: str = "enriched_coins.json",
                    batch_size: int = 300, exchange_delay: float = 0.12):
    if not os.path.exists(coins_file):
        print("ERROR: coins.json not found — run with --fetch first.")
        return

    with open(coins_file, "r", encoding="utf-8") as f:
        coins = json.load(f)
    total = len(coins)
    print(f"Auto-enrich starting: {total} coins; batch_size={batch_size}")

    # resume previously enriched if file exists
    enriched: List[Dict] = []
    if os.path.exists(enriched_file):
        try:
            with open(enriched_file, "r", encoding="utf-8") as f:
                enriched = json.load(f)
            print(f"[resume] {len(enriched)} already enriched; resuming from {len(enriched)}")
        except Exception:
            enriched = []

    start = len(enriched)
    i = start
    session = requests.Session()

    while i < total:
        end = min(total, i + batch_size)
        print(f"Processing batch {i+1} .. {end} ...")
        slice_coins = coins[i:end]
        batch_result = enrich_batch(slice_coins, exchange_delay=exchange_delay)
        enriched.extend(batch_result)

        # save after every batch (safe checkpoint)
        try:
            with open(enriched_file, "w", encoding="utf-8") as f:
                json.dump(enriched, f, ensure_ascii=False, indent=2)
            print(f"Saved enriched {len(enriched)}/{total} -> {enriched_file}")
        except Exception as e:
            print("Warning: failed to save enriched file:", e)

        i = end
        # small rest between batches
        time.sleep(0.6)

    print("Auto-enrich complete. Final enriched file:", enriched_file)


def quick_stats(coins_file: str = "coins.json", enriched_file: str = "enriched_coins.json"):
    if os.path.exists(coins_file):
        with open(coins_file, "r", encoding="utf-8") as f:
            coins = json.load(f)
        print(f"coins.json records: {len(coins)}")
    else:
        print("coins.json not present")

    if os.path.exists(enriched_file):
        with open(enriched_file, "r", encoding="utf-8") as f:
            enriched = json.load(f)
        total = len(enriched)
        with_bin = sum(1 for x in enriched if x.get("binance_pair"))
        with_cb = sum(1 for x in enriched if x.get("coinbase_pair"))
        print(f"enriched_coins.json records: {total} | with binance_pair: {with_bin} | with coinbase_pair: {with_cb}")
    else:
        print("enriched_coins.json not present")


def main():
    parser = argparse.ArgumentParser(description="Final multi_fetcher (fetch + auto-batch enrich)")
    parser.add_argument("--fetch", action="store_true", help="Fetch coins from CMC (resume safe)")
    parser.add_argument("--limit", type=int, default=5000, help="items per CMC request")
    parser.add_argument("--delay", type=float, default=1.0, help="delay between CMC requests")
    parser.add_argument("--auto-enrich", action="store_true", help="Run auto-batch exchange probing")
    parser.add_argument("--batch-size", type=int, default=300, help="Batch size for enrichment (phone-friendly)")
    parser.add_argument("--exchange-delay", type=float, default=0.12, help="Delay between probes inside batch")
    parser.add_argument("--stats", action="store_true", help="Show quick stats about coins/enriched files")
    args = parser.parse_args()

    if args.fetch:
        fetch_all_coins(limit=args.limit, delay_seconds=args.delay)
    if args.auto_enrich:
        auto_enrich_all(batch_size=args.batch_size, exchange_delay=args.exchange_delay)
    if args.stats:
        quick_stats()


if __name__ == "__main__":
    main()