from snl100.data_loader import generate_sample_data
from snl100.signal_engine import generate_signal
from snl100.plotter import plot_signal
from snl100.utils import save_signal_to_csv
from snl100.dashboard_builder import build_dashboard_html

def scan_all_symbols():
    symbols = ["BTCUSDT", "ETHUSDT", "XRPUSDT", "BNBUSDT", "SOLUSDT"]

    for symbol in symbols:
        print(f"🔍 در حال اسکن: {symbol}")
        df = generate_sample_data("up", 60)  # بعداً جایگزین با داده واقعی
        signal = generate_signal(df)
        plot_signal(df, signal, symbol=symbol, output_path=f"output/{symbol}_chart.html")
        save_signal_to_csv(signal, symbol=symbol)

    build_dashboard_html()
    print("✅ اسکن روزانه کامل شد.")

if __name__ == "__main__":
    scan_all_symbols()

