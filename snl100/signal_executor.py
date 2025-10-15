import math

def _safe(row, key):
    v = row.get(key)
    if v is None:
        return None
    try:
        f = float(v)
        if math.isnan(f):
            return None
        return f
    except Exception:
        return None

def decide_signal_from_indicators(row):
    price = _safe(row, "price")
    rsi = _safe(row, "rsi")
    ma_fast = _safe(row, "ma_fast")
    ma_slow = _safe(row, "ma_slow")
    vol = _safe(row, "volatility")
    macd = _safe(row, "macd")
    macd_signal = _safe(row, "macd_signal")

    if price is None:
        return {"signal": "hold", "target": None, "stop": None, "strategy": "NoPrice", "confidence": 0.0}

    # Strategy A: RSI extremes
    if rsi is not None:
        if rsi < 30:
            return {"signal": "buy", "target": price * 1.01, "stop": price * 0.99, "strategy": "RSI<30", "confidence": 0.7}
        if rsi > 70:
            return {"signal": "sell", "target": price * 0.99, "stop": price * 1.01, "strategy": "RSI>70", "confidence": 0.7}

    # Strategy B: MA crossover
    if ma_fast is not None and ma_slow is not None:
        if ma_fast > ma_slow:
            return {"signal": "buy", "target": price * 1.015, "stop": price * 0.985, "strategy": "MAfast>MAslow", "confidence": 0.6}
        if ma_fast < ma_slow:
            return {"signal": "sell", "target": price * 0.985, "stop": price * 1.015, "strategy": "MAfast<MAslow", "confidence": 0.6}

    # Strategy C: MACD cross
    if macd is not None and macd_signal is not None:
        if macd > macd_signal:
            return {"signal": "buy", "target": price * 1.012, "stop": price * 0.988, "strategy": "MACD>Signal", "confidence": 0.55}
        if macd < macd_signal:
            return {"signal": "sell", "target": price * 0.988, "stop": price * 1.012, "strategy": "MACD<Signal", "confidence": 0.55}

    # High volatility → avoid
    if vol is not None and vol > 0.05:
        return {"signal": "hold", "target": price, "stop": price, "strategy": "HighVol→Hold", "confidence": 0.5}

    return {"signal": "hold", "target": price, "stop": price, "strategy": "NoClearSignal", "confidence": 0.4}

