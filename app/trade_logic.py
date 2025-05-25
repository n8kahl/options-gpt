from .polygon_price import get_ohlcv

def scan_trade(symbol, balance=5000, risk_pct=0.02):
    df = get_ohlcv(symbol)
    df["HL"] = df["High"] - df["Low"]
    df["HC"] = abs(df["High"] - df["Close"].shift(1))
    df["LC"] = abs(df["Low"] - df["Close"].shift(1))
    df["TR"] = df[["HL", "HC", "LC"]].max(axis=1)
    df["ATR_14"] = df["TR"].rolling(14).mean()
    df["MA_20"] = df["Close"].rolling(20).mean()
    df["MA_50"] = df["Close"].rolling(50).mean()

    latest = df.iloc[-1]
    close, atr, ma20, ma50 = latest["Close"], latest["ATR_14"], latest["MA_20"], latest["MA_50"]

    if close > ma20 > ma50:
        trend, option_type = "bullish", "call"
        strike = round(close + 1, -1)
        target = round(close + atr, 2)
        stop = round(close - 0.5 * atr, 2)
    elif close < ma20 < ma50:
        trend, option_type = "bearish", "put"
        strike = round(close - 1, -1)
        target = round(close - atr, 2)
        stop = round(close + 0.5 * atr, 2)
    else:
        return {"message": f"No clear trend on {symbol}. Hold cash."}

    risk = balance * risk_pct
    est_premium = 2.5
    contracts = max(1, int(risk / (est_premium * 100)))

    return {
        "symbol": symbol,
        "trend": trend,
        "type": option_type,
        "strike": strike,
        "target": target,
        "stop": stop,
        "contracts": contracts,
        "risk": round(risk, 2),
        "price": round(close, 2),
        "atr": round(atr, 2)
    }
