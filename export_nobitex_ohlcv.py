# export_nobitex_ohlcv.py
import os
from snl100.nobitex_loader import fetch_nobitex_klines

# نمادهای نوبیتکس (ریالی)
symbol_map = {
    "BTCUSDT": "bitcoin",
    "ETHUSDT": "ethereum",
    "DOGEUSDT": "dogecoin",
    "XRPUSDT": "ripple",
    "TRXUSDT": "tron",
    "SHIBAUSDT": "shiba",
    "BNBUSDT": "binancecoin",
    "USDTUSDT": "tether"
}

interval = "1h"
limit = 300
output_dir = "data"

def main():
    os.makedirs(output_dir, exist_ok=True)
    for out_symbol, nobitex_symbol in symbol_map.items():
        print(f"📡 دریافت داده برای {out_symbol} از Nobitex...")
        try:
            df = fetch_nobitex_klines(nobitex_symbol, interval=interval, limit=limit)
            if df.empty:
                print(f"⚠️ هیچ داده‌ای برای {out_symbol} دریافت نشد.")
                continue
            df["symbol"] = out_symbol
            output_path = os.path.join(output_dir, f"ohlcv_{out_symbol}.csv")
            df.to_csv(output_path, index=False)
            print(f"✅ ذخیره شد: {output_path}")
        except Exception as e:
            print(f"❌ خطا در دریافت {out_symbol}: {e}")

if __name__ == "__main__":
    main()

