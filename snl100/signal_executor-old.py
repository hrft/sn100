import math
import random

def decide_signal_from_indicators(row):
    price = float(row["price"])
    rsi = float(row["rsi"]) if not pd.isna(row.get("rsi")) else None
    ma_fast = float(row["ma_fast"]) if not pd.isna(row.get("ma_fast")) else None
    ma_slow = float(row["ma_slow"]) if not pd.isna(row.get("ma_slow")) else None
    vol = float(row["volatility"]) if not pd.isna(row.get("volatility")) else None

    # Strategy 1: RSI extremes
    if rsi is not None:
        if rsi < 30:
            return {"signal": "buy", "target": price * 1.01, "stop": price * 0.99, "strategy": "RSI<30", "confidence": 0.7}
        elif rsi > 70:
            return {"signal": "sell", "target": price * 0.99, "stop": price * 1.01, "strategy": "RSI>70", "confidence": 0.7}

    # Strategy 2: MA crossover
    if ma_fast is not None and ma_slow is not None:
        if ma_fast > ma_slow:
            return {"signal": "buy", "target": price * 1.015, "stop": price * 0.985, "strategy": "MAfast>MAslow", "confidence": 0.6}
        elif ma_fast < ma_slow:
            return {"signal": "sell", "target": price * 0.985, "stop": price * 1.015, "strategy": "MAfast<MAslow", "confidence": 0.6}

    # Strategy 3: High volatility = Avoid
    if vol is not None and vol > 0.05:
        return {"signal": "hold", "target": price, "stop": price, "strategy": "HighVol→Hold", "confidence": 0.5}

    return {"signal": "hold", "target": price, "stop": price, "strategy": "NoClearSignal", "confidence": 0.4}


def decide_signal(symbol, price, orderbook=None):
    """
    تصمیم‌گیری برای سیگنال بر اساس قیمت لحظه‌ای و نماد.
    خروجی: dict شامل signal، target، stop
    """

    thresholds = {
        "BTCIRT": 2000000000,
        "ETHIRT": 120000000,
        "BNBIRT": 10000000,
        "XRPIRT": 15000,
        "DOGEIRT": 4000
    }

    base = thresholds.get(symbol, price)

    if price < base * 0.98:
        signal = "buy"
        target = price * 1.01
        stop = price * 0.99
    elif price > base * 1.02:
        signal = "sell"
        target = price * 0.99
        stop = price * 1.01
    else:
        signal = "hold"
        target = price
        stop = price

    return {
        "signal": signal,
        "target": round(target, 4),
        "stop": round(stop, 4)
    }


def decide_signal_with_rsi(symbol, price, rsi_value):
    """
    استراتژی مبتنی بر RSI:
    - RSI < 30 → buy
    - RSI > 70 → sell
    - در غیر این صورت → hold
    """
    if rsi_value < 30:
        return {"signal": "buy", "target": price * 1.01, "stop": price * 0.99}
    elif rsi_value > 70:
        return {"signal": "sell", "target": price * 0.99, "stop": price * 1.01}
    else:
        return {"signal": "hold", "target": price, "stop": price}

def decide_signal_mock(symbol, price):
    """
    نسخهٔ تستی برای تست سریع بدون منطق واقعی
    """
    signal = random.choice(["buy", "sell", "hold"])
    target = price * (1.01 if signal == "buy" else 0.99)
    stop = price * (0.99 if signal == "buy" else 1.01)
    return {
        "signal": signal,
        "target": round(target, 4),
        "stop": round(stop, 4)
    }

