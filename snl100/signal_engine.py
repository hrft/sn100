import pandas as pd

def generate_signal(df):
    """
    تولید سیگنال خرید یا فروش بر اساس:
    - MA50
    - شکست سقف/کف ۲۰ کندل اخیر
    - حجم آخر بیشتر از میانگین حجم ۲۰ کندل اخیر
    """

    if df is None or len(df) < 50:
        return {"signal": None, "entry": None, "stop": None, "target": None}

    df = df.copy()
    df["MA50"] = df["Close"].rolling(window=50).mean()
    df["VolMA20"] = df["Volume"].rolling(window=20).mean()

    last = df.iloc[-1]
    prev20 = df.iloc[-21:-1]

    # شرط خرید
    if last["Close"] > last["MA50"]:
        breakout = last["Close"] > prev20["High"].max()
        vol_ok = last["Volume"] > last["VolMA20"]
        if breakout and vol_ok:
            entry = round(last["Close"], 2)
            stop = round(prev20["Low"].min(), 2)
            target = round(entry + (entry - stop), 2)
            return {"signal": "buy", "entry": entry, "stop": stop, "target": target}

    # شرط فروش
    if last["Close"] < last["MA50"]:
        breakdown = last["Close"] < prev20["Low"].min()
        vol_ok = last["Volume"] > last["VolMA20"]
        if breakdown and vol_ok:
            entry = round(last["Close"], 2)
            stop = round(prev20["High"].max(), 2)
            target = round(entry - (stop - entry), 2)
            return {"signal": "sell", "entry": entry, "stop": stop, "target": target}

    print(f"🔎 بررسی {df.iloc[-1]['Date']}: Close={last['Close']}, MA50={last['MA50']}, High20={prev20['High'].max()}, Low20={prev20['Low'].min()}, Vol={last['Volume']}, VolMA20={last['VolMA20']}")

    return {"signal": None, "entry": None, "stop": None, "target": None}

