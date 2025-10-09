from snl100.signal_engine import generate_signal
from snl100.plotter import plot_signal
from snl100.utils import save_signal_to_csv
from snl100.dashboard_builder import build_dashboard_html
from snl100.symbol_filter import filter_symbols
from snl100.nobitex_loader import fetch_nobitex_klines
from snl100.binance_loader import fetch_binance_klines

def scan_all_symbols():
    all_symbols = ["BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT", "BNBUSDT", "DOGEUSDT"]

    # فیلتر اولیه با نوبیتکس چون قرار است در نوبیتکس اجرا کنی
    selected = filter_symbols(all_symbols, source="nobitex", interval="1h", limit=300,
                              min_quote_volume=20000, min_volatility=0.01)

    for symbol in selected:
        print(f"🔍 در حال اسکن و ساخت سیگنال برای: {symbol}")
        # برای سیگنال‌سازی می‌تونی از داده 15m استفاده کنی اما از همان اکسچنج نوبیتکس بگیر
        df = fetch_nobitex_klines(symbol=symbol, interval="15m", limit=200)
        signal = generate_signal(df)
        plot_signal(df, signal, symbol=symbol, output_path=f"output/{symbol}_chart.html")
        save_signal_to_csv(signal, symbol=symbol)

        # مقایسه‌ای: داده بایننس را هم بگیر و در صورت تمایل ذخیره کن (اختیاری)
        try:
            df_b = fetch_binance_klines(symbol=symbol.replace("/",""), interval="15m", limit=200)
            # می‌توانی اختلاف قیمت یا حجم را ذخیره کنی یا لاگ بگیری
        except Exception:
            pass

    build_dashboard_html()
    print("✅ اسکن روزانه کامل شد.")

if __name__ == "__main__":
    scan_all_symbols()

