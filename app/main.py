from fastapi import FastAPI, Query
from .trade_logic import scan_trade

app = FastAPI()

@app.get("/trade-suggestion")
def trade_suggestion(symbol: str = Query(...), balance: float = Query(5000)):
    result = scan_trade(symbol.upper(), balance)
    return result

from .polygon_options import get_options_snapshot

@app.get("/options-chain")
def options_chain(
    symbol: str,
    expiry: str = None,
    option_type: str = None,
    min_delta: float = None,
    max_delta: float = None
):
    results = get_options_snapshot(
        symbol, expiry=expiry,
        option_type=option_type,
        min_delta=min_delta,
        max_delta=max_delta
    )
    return {"contracts": results}

from .polygon_macro import get_macro_data

@app.get("/macro-data")
def macro_data():
    return get_macro_data()