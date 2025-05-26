import requests
import os

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

def get_options_snapshot(symbol, expiry=None, option_type="call", min_delta=0.3, max_delta=None):
    url = f"https://api.polygon.io/v3/snapshot/options/{symbol}?apiKey={POLYGON_API_KEY}"
    response = requests.get(url)
    raw = response.json()

    results = raw.get("results", [])
    print(f"🧾 Total contracts received from Polygon: {len(results)}")

    if results:
        print("🔍 Sample contract:", results[0])

    contracts = []

    for c in results:
        try:
            details = c.get("details", {})
            greeks = c.get("greeks", {})
            delta = greeks.get("delta")
            iv = c.get("implied_volatility")
            oi = c.get("open_interest")

            # Soft checks
            contract_type = details.get("contract_type", "").lower()
            if option_type and contract_type != option_type.lower():
                continue
            if min_delta and (delta is None or delta < min_delta):
                continue
            if max_delta and (delta is None or delta > max_delta):
                continue

            print(f"✅ Including: {details.get('ticker')} | Δ={delta}, IV={iv}, OI={oi}")

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
            print(f"⚠️ Skipping contract due to error: {e}")

    print(f"📦 Final contracts returned: {len(contracts)}")
    return contracts