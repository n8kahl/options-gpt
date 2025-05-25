import os, requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("POLYGON_API_KEY")

def get_options_snapshot(symbol, expiry=None, option_type=None, min_delta=None, max_delta=None):
    url = f"https://api.polygon.io/v3/snapshot/options/{symbol.upper()}?apiKey={API_KEY}"
    res = requests.get(url).json()
    contracts = res.get("results", [])

    filtered = []
    for c in contracts:
        o = c.get("details", {})
        g = c.get("greeks", {})
        t = c.get("last_quote", {})

        # Skip if missing data
        if not all(k in g for k in ("delta", "implied_volatility")):
            continue

        # Apply filters
        if expiry and o.get("expiration_date") != expiry:
            continue
        if option_type and o.get("contract_type") != option_type.upper():
            continue
        if min_delta and g.get("delta", 0) < float(min_delta):
            continue
        if max_delta and g.get("delta", 0) > float(max_delta):
            continue

        filtered.append({
            "symbol": o.get("ticker"),
            "strike": o.get("strike_price"),
            "expiration": o.get("expiration_date"),
            "type": o.get("contract_type"),
            "delta": round(g.get("delta", 0), 2),
            "iv": round(g.get("implied_volatility", 0), 4),
            "theta": round(g.get("theta", 0), 2),
            "gamma": round(g.get("gamma", 0), 2),
            "vega": round(g.get("vega", 0), 2),
            "bid": t.get("bid"),
            "ask": t.get("ask"),
            "open_interest": c.get("open_interest"),
            "volume": c.get("day", {}).get("volume")
        })

    return filtered