import requests
import pandas as pd
import os
from datetime import datetime

# نمادهای دلاری مورد نظر
symbols = [
    "BTCUSDT", "ETHUSDT", "DOGEUSDT", "XRPUSDT",
    "TRXUSDT", "SHIBUSDT", "BNBUSDT", "PEPEUSDT"
]

# نگاشت به نمادهای CryptoCompare
symbol_map = {
    "BTCUSDT": ("BTC", "USDT"),
    "ETHUSDT": ("ETH", "USDT"),
    "DOGEUSDT": ("DOGE", "USDT"),
    "XRPUSDT": ("XRP", "USDT"),
    "TRXUSDT": ("TRX", "USDT"),
    "SHIBUSDT": ("SHIB", "USDT"),
    "BNBUSDT": ("BNB", "USDT"),
    "PEPEUSDT": ("PEPE", "USDT")
}

limit = 200  # تعداد کندل‌ها
output_dir = "data"

def fetch_ohlcv(fsym, tsym):
    url = "https://min-api.cryptocompare.com/data/v2/histohour"
    params = {
        "fsym": fsym,
        "tsym": tsym,
        "limit": limit
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    raw = data.get("Data", {}).get("Data", [])
    if not raw:
        raise ValueError("No data returned")

    df = pd.DataFrame(raw)
    df["Date"] = pd.to_datetime(df["time"], unit="s")
    df = df.rename(columns={
        "open": "Open", "high": "High", "low": "Low",
        "close": "Close", "volumefrom": "Volume"
    })
    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]
    df[["Open", "High", "Low", "Close", "Volume"]] = df[["Open", "High", "Low", "Close", "Volume"]].astype(float)
    df["Date"] = pd.to_datetime(df["Date"])
    return df

def main():
    os.makedirs(output_dir, exist_ok=True)
    for symbol in symbols:
        fsym, tsym = symbol_map[symbol]
        print(f"📡 دریافت داده برای {symbol} از CryptoCompare...")
        try:
            df = fetch_ohlcv(fsym, tsym)
            df["symbol"] = symbol
            output_path = os.path.join(output_dir, f"ohlcv_{symbol}.csv")
            df.to_csv(output_path, index=False)
            print(f"✅ ذخیره شد: {output_path}")
        except Exception as e:
            print(f"❌ خطا در دریافت {symbol}: {e}")

if __name__ == "__main__":
    main()

