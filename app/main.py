from fastapi import FastAPI, Query
from .trade_logic import scan_trade

app = FastAPI()

from fastapi.openapi.utils import get_openapi

app = FastAPI()

@app.get("/openapi.json")
def custom_openapi():
    openapi_schema = get_openapi(
        title="Options GPT API",
        version="1.0.0",
        description="Live options analysis and macro data",
        routes=app.routes,
    )
    openapi_schema["servers"] = [
        {
            "url": "https://options-gpt.onrender.com",
            "description": "Production server"
        }
    ]
    return openapi_schema
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

from fastapi.staticfiles import StaticFiles
import os

# Mount the .well-known directory to serve ai-plugin.json
if os.path.isdir(".well-known"):
    app.mount("/.well-known", StaticFiles(directory=".well-known"), name="well-known")

    from app.polygon_options import router as polygon_router
app.include_router(polygon_router)