from fastapi import FastAPI, Query
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
import os

from .trade_logic          import scan_trade
from .polygon_options      import get_options_snapshot, router as options_router
from .polygon_macro        import get_macro_data
from .polygon_technicals   import router as technicals_router

app = FastAPI()

@app.get("/openapi.json")
def custom_openapi():
    oas = get_openapi(
        title="Options GPT API",
        version="1.0.0",
        description="Live options analysis, macro data & technicals",
        routes=app.routes,
    )
    oas["servers"] = [{"url":"https://options-gpt.onrender.com"}]
    return oas

@app.get("/trade-suggestion")
def trade_suggestion(symbol: str = Query(...), balance: float = Query(5000)):
    return scan_trade(symbol.upper(), balance)

@app.get("/options-chain")
def options_chain(
    symbol: str,
    expiry: str = None,
    option_type: str = None,
    min_delta: float = None,
    max_delta: float = None
):
    return {"contracts": get_options_snapshot(
        symbol, expiry, option_type, min_delta, max_delta
    )}

@app.get("/macro-data")
def macro_data():
    return get_macro_data()

# Serve plugin manifest
if os.path.isdir(".well-known"):
    app.mount("/.well-known",
        StaticFiles(directory=".well-known"),
        name="well-known"
    )

# Mount routers
app.include_router(options_router)
app.include_router(technicals_router)