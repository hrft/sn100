import requests
import pandas as pd
import os
from datetime import datetime

# نمادهای دلاری مورد نظر
target_symbols = [
    "BTCUSDT", "ETHUSDT", "DOGEUSDT", "XRPUSDT",
    "TRXUSDT", "SHIBUSDT", "BNBUSDT", "PEPEUSDT",
    "XMRUSDT", "LINAUSDT", "XVSUSDT", "TRUSTUSDT"
]

interval = "1h"
limit = 300
output_dir = "data"

def get_valid_symbols():
    url = "https://api.mexc.com/api/v3/exchangeInfo"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    info = r.json()
    return set(s["symbol"] for s in info.get("symbols", []))

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
    print("📡 دریافت لیست نمادهای معتبر از MEXC...")
    try:
        valid_symbols = get_valid_symbols()
    except Exception as e:
        print(f"❌ خطا در دریافت لیست نمادها: {e}")
        return

    for symbol in target_symbols:
        if symbol not in valid_symbols:
            print(f"⚠️ نماد نامعتبر یا غیرفعال در MEXC: {symbol}")
            continue
        print(f"📡 دریافت داده برای {symbol}...")
        try:
            df = fetch_ohlcv(symbol)
            output_path = os.path.join(output_dir, f"ohlcv_{symbol}.csv")
            df.to_csv(output_path, index=False)
            print(f"✅ ذخیره شد: {output_path}")
        except Exception as e:
            print(f"❌ خطا در دریافت {symbol}: {e}")

if __name__ == "__main__":
    main()

