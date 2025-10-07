import pandas as pd

def generate_signal(df, risk_ratio=2.0):
    """
    تولید سیگنال خرید/فروش بر اساس شکست + حجم + MA50
    """
    df = df.copy()
    df['MA50'] = df['Close'].rolling(50).mean()
    df['VolMA20'] = df['Volume'].rolling(20).mean()

    last = df.iloc[-1]
    prev20 = df.iloc[-20:]

    signal = None
    entry = stop = target = None

    # سیگنال خرید
    if last['Close'] > last['MA50']:
        breakout = last['Close'] > prev20['High'].max()
        vol_ok = last['Volume'] > last['VolMA20']
        if breakout and vol_ok:
            signal = "buy"
            entry = last['Close']
            stop = prev20['Low'].min()
            risk = entry - stop
            target = entry + risk * risk_ratio

    # سیگنال فروش
    elif last['Close'] < last['MA50']:
        breakout = last['Close'] < prev20['Low'].min()
        vol_ok = last['Volume'] > last['VolMA20']
        if breakout and vol_ok:
            signal = "sell"
            entry = last['Close']
            stop = prev20['High'].max()
            risk = stop - entry
            target = entry - risk * risk_ratio

    return {
        "signal": signal,
        "entry": round(entry, 2) if entry else None,
        "stop": round(stop, 2) if stop else None,
        "target": round(target, 2) if target else None
    }

