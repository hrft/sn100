import os
import requests
import pandas as pd

# نمادها
symbols = ['BTC', 'ETH', 'BNB', 'SHIB', 'PEPE']

# مسیر خروجی: پوشه data کنار همین فایل
output_dir = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(output_dir, exist_ok=True)

# آدرس API
base_url = 'https://min-api.cryptocompare.com/data/v2/histohour'

def fetch_ohlcv(symbol):
    params = {
        'fsym': symbol,
        'tsym': 'USDT',
        'limit': 199
    }
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        if data['Response'] != 'Success':
            print(f"❌ خطا در دریافت داده برای {symbol}: {data.get('Message', 'Unknown error')}")
            return

        rows = data['Data']['Data']
        df = pd.DataFrame(rows)
        df['Date'] = pd.to_datetime(df['time'], unit='s')
        df['symbol'] = symbol

        # ذخیره هر دو ستون حجم
        df = df[['Date', 'open', 'high', 'low', 'close', 'volumefrom', 'volumeto', 'symbol']]
        df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'VolumeFrom', 'VolumeTo', 'symbol']

        filename = os.path.join(output_dir, f"ohlcv_{symbol}.csv")
        df.to_csv(filename, index=False, encoding="utf-8")
        print(f"✅ ذخیره شد: {filename}")

    except Exception as e:
        print(f"⚠️ خطا در پردازش {symbol}: {e}")

# اجرای اصلی
if __name__ == "__main__":
    for sym in symbols:
        fetch_ohlcv(sym)

