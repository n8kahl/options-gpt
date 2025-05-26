import requests
import os

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

def get_options_snapshot(symbol, expiry=None, option_type=None, min_delta=None, max_delta=None):
    url = f"https://api.polygon.io/v3/snapshot/options/{symbol}?apiKey={POLYGON_API_KEY}"
    res = requests.get(url)
    raw = res.json()

    contracts = []

    for c in raw.get("results", []):
        try:
            details = c.get("details", {})
            greeks = c.get("greeks", {})
            delta = greeks.get("delta")
            iv = c.get("implied_volatility")
            oi = c.get("open_interest")

            if option_type and details.get("contract_type", "").lower() != option_type.lower():
                continue
            if min_delta and (delta is None or delta < min_delta):
                continue
            if max_delta and (delta is None or delta > max_delta):
                continue

            contracts.append({
                "symbol": details.get("ticker"),
                "strike": details.get("strike_price"),
                "expiration": details.get("expiration_date"),
                "delta": round(delta, 3) if delta else None,
                "iv": round(iv, 3) if iv else None,
                "open_interest": oi,
                "bid": c.get("day", {}).get("bid"),
                "ask": c.get("day", {}).get("ask")
            })
        except Exception as e:
            print(f"Skipping contract due to error: {e}")

    return contracts