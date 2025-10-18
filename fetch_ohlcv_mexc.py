import requests
import pandas as pd
import os
from datetime import datetime

# نمادهای دلاری مورد نظر
symbols = [
    "BTCUSDT", "ETHUSDT", "DOGEUSDT", "XRPUSDT",
    "TRXUSDT", "SHIBUSDT", "BNBUSDT", "PEPEUSDT"
]

interval = "1h"  # تایم‌فریم: 1m, 5m, 15m, 1h, 4h, 1d
limit = 300      # تعداد کندل‌ها
output_dir = "data"

def fetch_ohlcv(symbol):
    url = "https://api.mexc.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    raw = r.json()

    df = pd.DataFrame(raw, columns=[
        "OpenTime", "Open", "High", "Low", "Close", "Volume",
        "CloseTime", "QuoteVolume", "Trades", "TakerBuyBase", "TakerBuyQuote", "Ignore"
    ])
    df["Date"] = pd.to_datetime(df["OpenTime"], unit="ms")
    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]
    df = df.astype({"Open": float, "High": float, "Low": float, "Close": float, "Volume": float})
    df["symbol"] = symbol
    return df

def main():
    os.makedirs(output_dir, exist_ok=True)
    for symbol in symbols:
        print(f"📡 دریافت داده برای {symbol} از MEXC...")
        try:
            df = fetch_ohlcv(symbol)
            output_path = os.path.join(output_dir, f"ohlcv_{symbol}.csv")
            df.to_csv(output_path, index=False)
            print(f"✅ ذخیره شد: {output_path}")
        except Exception as e:
            print(f"❌ خطا در دریافت {symbol}: {e}")

if __name__ == "__main__":
    main()

