import requests
import csv
import os
from datetime import datetime, timedelta

symbol = "ETHUSDT"
resolution = "1h"  # تایم‌فریم: 1h, 15m, 1d
hours_back = 48    # چند ساعت گذشته رو بگیریم
output_file = f"data/ohlcv_{symbol}.csv"

# گرفتن توکن و آدرس از محیط
api_base = os.getenv("NOBITEX_API_BASE", "https://apiv2.nobitex.ir")
token = os.getenv("NOBITEX_TOKEN")

def fetch_candles():
    to_ts = int(datetime.now().timestamp())
    from_ts = int((datetime.now() - timedelta(hours=hours_back)).timestamp())
    url = f"{api_base}/market/candles"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "symbol": symbol,
        "resolution": resolution,
        "from": from_ts,
        "to": to_ts
    }

    print(f"📡 دریافت کندل‌های {resolution} از Nobitex برای {symbol}...")
    r = requests.post(url, json=payload, headers=headers)
    if "application/json" not in r.headers.get("Content-Type", ""):
        print("⚠️ پاسخ JSON نیست. محتوا:")
        print(r.text)
        return []

    try:
        data = r.json()
        return data.get("candles", [])
    except Exception as e:
        print(f"⚠️ خطا در تبدیل JSON: {e}")
        print(r.text)
        return []

def save_csv(candles):
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "symbol", "open", "high", "low", "close", "volume"])
        for c in candles:
            ts = datetime.fromtimestamp(c[0]).strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([ts, symbol, c[1], c[2], c[3], c[4], c[5]])
    print(f"✅ ذخیره شد: {output_file}")

def main():
    candles = fetch_candles()
    if not candles:
        print("⚠️ هیچ داده‌ای دریافت نشد.")
        return
    save_csv(candles)

if __name__ == "__main__":
    main()

