import os
import json
from snl100.symbol_filter import filter_symbols_nobitex
from snl100.nobitex_api import fetch_candles_or_trades
from snl100.nobitex_orderbook import orderbook_liquidity_metrics
from snl100.signal_engine import generate_signal
from snl100.plotter import plot_signal
from snl100.utils import save_signal_to_csv
from snl100.dashboard_builder import build_dashboard_html

MARKETS = ["ETHUSDT", "XRPUSDT", "SOLUSDT", "BNBUSDT", "DOGEUSDT"]

def fixed_entry_logic(market, metrics):
    mid = metrics.get("mid_price")
    entry = {
        "Time": "now",
        "Symbol": market,
        "Signal": "entry",
        "Entry": mid,
        "Stop": round(mid * 0.98, 4),   # –2%
        "Target": round(mid * 1.03, 4), # +3%
        "Chart": f"signals/{market}_chart.html"
    }
    return entry

def scan_all_symbols_v1():
    os.makedirs("output", exist_ok=True)
    os.makedirs("output/signals", exist_ok=True)

    selected, details = filter_symbols_nobitex(
        MARKETS,
        min_top_quote=15000,
        per_symbol_thresholds={"BNBUSDT": 8000, "XRPUSDT": 5000, "DOGEUSDT": 5000},
        top_n_depth=12,
        require_trend=True,
        allow_orderbook_only=True
    )

    with open("output/filter_details_v1.json", "w", encoding="utf-8") as f:
        json.dump(details, f, ensure_ascii=False, indent=2)

    for d in details:
        market = d["market"]
        reason = d.get("reason")
        print(f"🔍 [v1] Processing {market} → reason={reason}")
        if not d.get("ok"):
            continue

        if reason == "trend_ok_with_candles":
            df = fetch_candles_or_trades(market, interval="15", limit=500, days=5)
            if df is None or df.empty:
                print(f"⚠️ کندل برای {market} نیومد، می‌ریم سراغ درصد ثابت")
                entry = fixed_entry_logic(market, d.get("metrics", {}))
                save_signal_to_csv(entry, symbol=market)
                continue
            signal = generate_signal(df)
            chart_path = f"output/signals/{market}_chart.html"
            plot_signal(df, signal, symbol=market, output_path=chart_path)
            if isinstance(signal, dict):
                signal["Chart"] = f"signals/{market}_chart.html"
            save_signal_to_csv(signal, symbol=market)
        else:
            entry = fixed_entry_logic(market, d.get("metrics", {}))
            chart_path = f"output/signals/{market}_chart.html"
            plot_signal(None, None, symbol=market, output_path=chart_path)
            save_signal_to_csv(entry, symbol=market)

    build_dashboard_html()
    print("✅ [v1] اسکن کامل شد و داشبورد ساخته شد: output/dashboard.html")

if __name__ == "__main__":
    scan_all_symbols_v1()

