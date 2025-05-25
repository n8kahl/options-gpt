import os, requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("POLYGON_API_KEY")

def get_ohlcv(symbol, days=30):
    end = datetime.now()
    start = end - timedelta(days=days)
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start.date()}/{end.date()}?adjusted=true&sort=asc&limit={days}&apiKey={API_KEY}"
    res = requests.get(url).json()
    df = pd.DataFrame(res.get("results", []))
    df["date"] = pd.to_datetime(df["t"], unit="ms")
    df.set_index("date", inplace=True)
    df["Close"] = df["c"]
    df["High"] = df["h"]
    df["Low"] = df["l"]
    return df
