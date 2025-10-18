import requests
import pandas as pd
import os
from datetime import datetime

# نگاشت نمادهای دلاری به شناسه‌های Coingecko
symbol_map = {
    "BTCUSDT": "bitcoin",
    "ETHUSDT": "ethereum",
    "DOGEUSDT": "dogecoin",
    "XRPUSDT": "ripple",
    "TRXUSDT": "tron",
    "SHIBUSDT": "shiba-inu",
    "BNBUSDT": "binancecoin",
    "PEPEUSDT": "pepe"
}

vs_currency = "usd"
days = 7  # چند روز گذشته
interval = "hourly"  # تایم‌فریم: 'hourly' یا 'daily'
output_dir = "data"

def fetch_ohlcv(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": vs_currency,
        "days": days,
        "interval": interval
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    prices = data.get("prices", [])
    volumes = data.get("total_volumes", [])

    df = pd.DataFrame(prices, columns=["timestamp", "Close"])
    df["Volume"] = [v[1] for v in volumes]
    df["Date"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["Open"] = df["Close"].shift(1)
    df["High"] = df["Close"].rolling(2).max()
    df["Low"] = df["Close"].rolling(2).min()
    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]
    df = df.dropna().astype(float)
    return df

def main():
    os.makedirs(output_dir, exist_ok=True)
    for symbol, coin_id in symbol_map.items():
        print(f"📡 دریافت داده برای {symbol} از Coingecko...")
        try:
            df = fetch_ohlcv(coin_id)
            df["symbol"] = symbol
            output_path = os.path.join(output_dir, f"ohlcv_{symbol}.csv")
            df.to_csv(output_path, index=False)
            print(f"✅ ذخیره شد: {output_path}")
        except Exception as e:
            print(f"❌ خطا در دریافت {symbol}: {e}")

if __name__ == "__main__":
    main()

