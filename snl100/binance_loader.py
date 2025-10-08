import requests
import pandas as pd

def fetch_binance_klines(symbol="BTCUSDT", interval="15m", limit=60):
    url = f"https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    response = requests.get(url, params=params)
    data = response.json()

    df = pd.DataFrame(data, columns=[
        "OpenTime", "Open", "High", "Low", "Close", "Volume",
        "CloseTime", "QuoteAssetVolume", "Trades", "TakerBuyBase",
        "TakerBuyQuote", "Ignore"
    ])

    df["Date"] = pd.to_datetime(df["OpenTime"], unit="ms")
    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]
    df = df.astype({
        "Open": float, "High": float, "Low": float,
        "Close": float, "Volume": float
    })

    return df

