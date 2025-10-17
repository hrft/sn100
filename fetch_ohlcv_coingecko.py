# fetch_ohlcv_coingecko.py
import requests
import csv
from datetime import datetime

symbol = "bitcoin"  # یا ethereum, dogecoin, ...
vs_currency = "usd"
days = "1"  # چند روز گذشته (1، 7، 30، max)
interval = "minute"  # یا hourly, daily
output_file = "data/ohlcv.csv"

def fetch_and_save():
    url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart"
    params = {
        "vs_currency": vs_currency,
        "days": days,
        "interval": interval
    }
    print(f"📡 دریافت داده از Coingecko برای {symbol}...")
    r = requests.get(url, params=params)
    data = r.json()

    prices = data.get("prices", [])
    volumes = data.get("total_volumes", [])

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
            writer.writerow([ts, symbol.upper(), round(open_, 2), round(high, 2), round(low, 2), round(close, 2), round(volume, 2)])

    print(f"✅ ذخیره شد: {output_file}")

if __name__ == "__main__":
    fetch_and_save()

