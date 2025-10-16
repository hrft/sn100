import pandas as pd
from collections import deque
from snl100.data_collector import fetch_price, check_all_sources
from snl100.indicator_engine import enrich_dataframe
from snl100.signal_executor import decide_signal_from_indicators

SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT"]
WINDOW = 20
MEMORY = {s: deque(maxlen=WINDOW) for s in SYMBOLS}

def get_signal(symbol):
    health = check_all_sources(symbol)
    if not (health["nobitex"] or health["tabdeal"]):
        print(f"⚠️ SourceDown for {symbol}: {health}")
        return {
            "symbol": symbol,
            "price": None,
            "signal": "hold",
            "target": None,
            "stop": None,
            "strategy": "SourceDown",
            "confidence": 0.0
        }

    price = fetch_price(symbol)
    if price is None:
        return {
            "symbol": symbol,
            "price": None,
            "signal": "hold",
            "target": None,
            "stop": None,
            "strategy": "PriceUnavailable",
            "confidence": 0.0
        }

    MEMORY[symbol].append(price)
    prices = list(MEMORY[symbol])

    if len(prices) < WINDOW:
        return {
            "symbol": symbol,
            "price": price,
            "signal": "hold",
            "target": price,
            "stop": price,
            "strategy": "InsufficientData",
            "confidence": 0.3
        }

    df = pd.DataFrame({"price": prices})
    enriched = enrich_dataframe(df)
    row = enriched.iloc[-1].to_dict()
    signal = decide_signal_from_indicators(row)
    signal.update({"symbol": symbol, "price": price})
    return signal

