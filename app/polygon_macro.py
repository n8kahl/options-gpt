import os, requests
from dotenv import load_dotenv

load_dotenv()
FRED_API_KEY = os.getenv("FRED_API_KEY")

def get_fred_data(series_id):
    url = (
        f"https://api.stlouisfed.org/fred/series/observations"
        f"?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json&sort_order=desc&limit=1"
    )
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching {series_id}: {response.text}")
        return None

    data = response.json().get("observations", [])
    if not data:
        return None

    latest = data[0]
    return {
        "value": float(latest["value"]),
        "date": latest["date"]
    }

def get_macro_data():
    indicators = {
        "CPI (All Items)": "CPIAUCSL",
        "Unemployment Rate": "UNRATE",
        "Real GDP": "GDPC1",
        "Fed Funds Rate": "FEDFUNDS"
    }

    macro_data = {}
    for name, series_id in indicators.items():
        result = get_fred_data(series_id)
        if result:
            macro_data[name] = result
        else:
            macro_data[name] = {"value": None, "date": None}

    return macro_data