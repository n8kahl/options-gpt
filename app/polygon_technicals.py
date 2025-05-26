import os
import requests
import pandas as pd
from fastapi import APIRouter, Query
from datetime import datetime, timedelta

router = APIRouter()
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

@router.get("/technicals")
def get_technicals(
    symbol: str = Query(..., description="Ticker, e.g. SPY or QQQ"),
    days: int   = Query(60,  description="Days of history"),
    sma_short: int = Query(20),
    sma_long:  int = Query(50),
    ema_short: int = Query(8),
    ema_long:  int = Query(21),
    rsi_period: int = Query(14),
    atr_period: int = Query(14),
):
    # 1) Fetch OHLC from Polygon
    end   = datetime.utcnow()
    start = end - timedelta(days=days)
    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/"
        f"{start.date()}/{end.date()}?adjusted=true"
        f"&limit={days}&apiKey={POLYGON_API_KEY}"
    )
    resp = requests.get(url).json().get("results", [])
    if not resp:
        return {"error": "No historical data returned."}

    df = pd.DataFrame(resp)
    df["date"]  = pd.to_datetime(df["t"], unit="ms")
    df.set_index("date", inplace=True)
    df["close"] = df["c"]
    df["high"]  = df["h"]
    df["low"]   = df["l"]

    # 2) Calculate SMA & EMA
    df["sma_short"] = df["close"].rolling(sma_short).mean()
    df["sma_long"]  = df["close"].rolling(sma_long).mean()
    df["ema_short"] = df["close"].ewm(span=ema_short, adjust=False).mean()
    df["ema_long"]  = df["close"].ewm(span=ema_long,  adjust=False).mean()

    # 3) RSI
    delta = df["close"].diff()
    gain  = delta.where(delta>0, 0).rolling(rsi_period).mean()
    loss  = -delta.where(delta<0, 0).rolling(rsi_period).mean()
    rs    = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))

    # 4) MACD
    exp1 = df["close"].ewm(span=12, adjust=False).mean()
    exp2 = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"]        = exp1 - exp2
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"]   = df["macd"] - df["macd_signal"]

    # 5) ATR
    hl = df["high"] - df["low"]
    hc = (df["high"] - df["close"].shift()).abs()
    lc = (df["low"]  - df["close"].shift()).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    df["atr"] = tr.rolling(atr_period).mean()

    # 6) VIX quote
    try:
        v = requests.get(
            f"https://api.polygon.io/v1/last_quote/CBOE:VIX?apiKey={POLYGON_API_KEY}"
        ).json().get("last", {}).get("price")
    except:
        v = None

    latest = df.iloc[-1]
    return {
        "symbol": symbol,
        "vix": round(v,2) if v else None,
        "sma_short": round(latest["sma_short"],2),
        "sma_long":  round(latest["sma_long"],2),
        "ema_short": round(latest["ema_short"],2),
        "ema_long":  round(latest["ema_long"],2),
        "rsi":       round(latest["rsi"],2),
        "macd":      round(latest["macd"],3),
        "macd_signal": round(latest["macd_signal"],3),
        "macd_hist":  round(latest["macd_hist"],3),
        "atr":        round(latest["atr"],2)
    }