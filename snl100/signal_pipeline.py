import pandas as pd
from snl100.config import USDT_SYMBOLS
from snl100.data_collector import fetch_price, check_source
from snl100.indicator_engine import enrich_dataframe
from snl100.signal_executor import decide_signal_from_indicators

# حافظهٔ ساده درون‌پروسه‌ای (بدون فایل)
MEMORY = {s: [] for s in USDT_SYMBOLS}
WINDOW = 20

def get_signal(symbol):
    # health check
    healthy = check_source(symbol)
    if not healthy:
        return {"symbol": symbol, "price": None, "signal": "hold", "target": None,
                "stop": None, "strategy": "SourceDown", "confidence": 0.0}

    price = fetch_price(symbol)
    if price is None:
        return {"symbol": symbol, "price": None, "signal": "hold", "target": None,
                "stop": None, "strategy": "PriceUnavailable", "confidence": 0.0}

    arr = MEMORY[symbol]
    arr.append(price)
    if len(arr) < WINDOW:
        return {"symbol": symbol, "price": price, "signal": "hold", "target": price,
                "stop": price, "strategy": "InsufficientData", "confidence": 0.3}

    df = pd.DataFrame({"price": arr[-WINDOW:]})
    enriched = enrich_dataframe(df)
    row = enriched.iloc[-1].to_dict()
    sig = decide_signal_from_indicators(row)
    sig.update({"symbol": symbol, "price": price})
    return sig

