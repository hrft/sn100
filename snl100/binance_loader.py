import requests
import pandas as pd

def fetch_binance_klines(symbol="BTCUSDT", interval="1h", limit=300):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame(data, columns=[
        "OpenTime","Open","High","Low","Close","Volume",
        "CloseTime","QuoteAssetVolume","Trades","TakerBuyBase",
        "TakerBuyQuote","Ignore"
    ])
    df["Date"] = pd.to_datetime(df["OpenTime"], unit="ms")
    df = df[["Date","Open","High","Low","Close","Volume","QuoteAssetVolume"]]
    df = df.rename(columns={"QuoteAssetVolume":"QuoteVolume"})
    df = df.astype({"Open":float,"High":float,"Low":float,"Close":float,"Volume":float,"QuoteVolume":float})
    # اگر QuoteVolume ناقص بود، محاسبه تقریبی
    if df["QuoteVolume"].isna().any():
        df["QuoteVolume"] = df["Volume"] * df["Close"]
    return df

