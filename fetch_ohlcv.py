# fetch_ohlcv.py
import ccxt
import csv
from datetime import datetime

# تنظیمات
exchange = ccxt.binance()  # برای Nobitex باید API جداگانه استفاده بشه
symbol = 'BTC/USDT'
timeframe = '5m'  # تایم‌فریم کندل‌ها
limit = 100       # تعداد کندل‌ها
output_file = 'data/ohlcv.csv'

def fetch_and_save():
    print(f"📡 دریافت داده برای {symbol} از {exchange.name}...")
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'volume'])
        for row in ohlcv:
            ts = datetime.utcfromtimestamp(row[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([ts, symbol.replace('/', ''), *row[1:]])
    print(f"✅ ذخیره شد: {output_file}")

if __name__ == '__main__':
    fetch_and_save()

