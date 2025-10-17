import requests
import csv
from datetime import datetime

symbol_id = "ethereum"
symbol_out = "ETHUSDT"
vs_currency = "usd"
days = "1"
output_file = "data/ohlcv.csv"

def fetch_and_save():
    url = f"https://api.coingecko.com/api/v3/coins/{symbol_id}/market_chart"
    params = {
        "vs_currency": vs_currency,
        "days": days
    }
    print(f"📡 دریافت داده از Coingecko برای {symbol_id}...")
    r = requests.get(url, params=params)
    data = r.json()

    prices = data.get("prices", [])
    volumes = data.get("total_volumes", [])

    if not prices:
        print("⚠️ هیچ داده‌ای دریافت نشد. بررسی پارامترها یا اتصال اینترنت.")
        return

    with open(output_file, "w", newline="", encoding="utf-8") as f:
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

    print(f"✅ ذخیره شد: {output_file}")

if __name__ == "__main__":
    fetch_and_save()

