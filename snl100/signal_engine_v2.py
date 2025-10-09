import pandas as pd
import ta  # از pandas-ta یا ta-lib استفاده کن

def generate_advanced_signal(df):
    if df is None or len(df) < 100:
        return {"signal": None, "entry": None, "stop": None, "target": None}

    df = df.copy()

    # محاسبه Ichimoku
    ichimoku = ta.trend.IchimokuIndicator(
        high=df["High"], low=df["Low"], window1=9, window2=26, window3=52
    )
    df["tenkan"] = ichimoku.ichimoku_conversion_line()
    df["kijun"] = ichimoku.ichimoku_base_line()
    df["senkou_a"] = ichimoku.ichimoku_a()
    df["senkou_b"] = ichimoku.ichimoku_b()

    last = df.iloc[-1]
    prev20 = df.iloc[-21:-1]

    # بررسی شکست سقف/کف
    breakout = last["Close"] > prev20["High"].max()
    breakdown = last["Close"] < prev20["Low"].min()

    # بررسی موقعیت قیمت نسبت به ابر
    above_kumo = last["Close"] > max(last["senkou_a"], last["senkou_b"])
    below_kumo = last["Close"] < min(last["senkou_a"], last["senkou_b"])

    # شرط خرید
    if breakout and above_kumo and last["tenkan"] > last["kijun"]:
        entry = round(last["Close"], 2)
        stop = round(prev20["Low"].min(), 2)
        target = round(entry + (entry - stop), 2)
        return {"signal": "strong_buy", "entry": entry, "stop": stop, "target": target}

    # شرط فروش
    if breakdown and below_kumo and last["tenkan"] < last["kijun"]:
        entry = round(last["Close"], 2)
        stop = round(prev20["High"].max(), 2)
        target = round(entry - (stop - entry), 2)
        return {"signal": "strong_sell", "entry": entry, "stop": stop, "target": target}

    print(f"📊 Close={last['Close']}, Tenkan={last['tenkan']}, Kijun={last['kijun']},SenkouA={last['senkou_a']}, SenkouB={last['senkou_b']}")
    return {"signal": None, "entry": None, "stop": None, "target": None}

