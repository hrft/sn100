import requests
import csv
from datetime import datetime
import os

# تنظیمات
symbols = {
    "BTCUSDT": "bitcoin",
    "ETHUSDT": "ethereum",
    "DOGEUSDT": "dogecoin",
    "XRPUSDT": "ripple",
    "BNBUSDT": "binancecoin"
}
vs_currency = "usd"
days = "7"           # تعداد روزها: 1, 7, 30, max
interval = "daily"   # فقط 'daily' یا 'hourly' معتبره
output_dir = "data"

def fetch_and_save(symbol_out, symbol_id):
    url = f"https://api.coingecko.com/api/v3/coins/{symbol_id}/market_chart"
    params = {
        "vs_currency": vs_currency,
        "days": days
    }
    print(f"📡 دریافت داده برای {symbol_out} از Coingecko...")
    r = requests.get(url, params=params)
    data = r.json()

    prices = data.get("prices", [])
    volumes = data.get("total_volumes", [])

    if not prices:
        print(f"⚠️ داده‌ای برای {symbol_out} دریافت نشد.")
        return

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"ohlcv_{symbol_out}.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "symbol", "open", "high", "low", "close", "volume"])
        for i in range(1, len(prices)):
            ts = datetime.utcfromtimestamp(prices[i][0] / 1000).strftime("%Y-%m-%d %H:%M:%S")
            open_ = prices[i-1][1]
            close = prices[i][1]
            high = max(open_, close)
            low = min(open_, close)
            volume = volumes[i][1] if i < len(volumes) else 0
            writer.writerow([ts, symbol_out, round(open_, 2), round(high, 2), round(low, 2), round(close, 2), round(volume, 2)])
    print(f"✅ ذخیره شد: {path}")

def main():
    for symbol_out, symbol_id in symbols.items():
        fetch_and_save(symbol_out, symbol_id)

if __name__ == "__main__":
    main()

