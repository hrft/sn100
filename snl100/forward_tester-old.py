import os
import csv
import time
import requests
import matplotlib.pyplot as plt
from datetime import datetime
from snl100.signal_executor import decide_signal
from snl100.indicator_engine import enrich_dataframe
from snl100.signal_executor import decide_signal_from_indicators

SYMBOLS = ["BTCIRT", "ETHIRT", "BNBIRT", "XRPIRT", "DOGEIRT"]
LOG_FILE = "output/forward_test_log.csv"
CHART_FILE = "output/forward_test_chart.png"

def ensure_dirs():
    os.makedirs("output", exist_ok=True)

def fetch_usdt_irt():
    try:
        url = "https://apiv2.nobitex.ir/v3/orderbook/USDTIRT"
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data["lastTradePrice"])
    except Exception as e:
        print(f"❌ خطا در دریافت نرخ USDTIRT: {e}")
        return None

def fetch_nobitex_price(symbol):
    try:
        url = f"https://apiv2.nobitex.ir/v3/orderbook/{symbol}"
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data["lastTradePrice"])
    except Exception as e:
        print(f"❌ Nobitex error for {symbol}: {e}")
        return None

def fetch_tabdeal_price(symbol):
    try:
        url = "https://api1.tabdeal.org/api/v1/rest/tickers"
        response = requests.get(url, timeout=5)
        data = response.json()
        for item in data["result"]:
            if item["symbol"].upper() == symbol:
                return float(item["last"])
        return None
    except Exception as e:
        print(f"❌ Tabdeal error for {symbol}: {e}")
        return None

def fetch_price_usdt(symbol):
    usdt_irt = fetch_usdt_irt()
    if not usdt_irt:
        print("⚠️ نرخ USDTIRT در دسترس نیست.")
        return None
    price_irt = fetch_nobitex_price(symbol)
    if price_irt is None:
        price_irt = fetch_tabdeal_price(symbol)
    if price_irt is None:
        return None
    return round(price_irt / usdt_irt, 4)

def generate_signal(symbol, price):
    decision = decide_signal(symbol, price)
    signal_type = decision["signal"]
    target = decision["target"]
    stop = decision["stop"]

    # شبیه‌سازی نتیجه فرضی
    hit = signal_type != "hold" and (target > price if signal_type == "buy" else target < price)
    result = "hit_target" if hit else "missed"
    profit = (target - price) if signal_type == "buy" else (price - target)
    profit = profit if result == "hit_target" else -abs(profit)

    return {
        "symbol": symbol,
        "price": price,
        "signal": signal_type,
        "target": round(target, 4),
        "result": result,
        "profit": round(profit, 4),
        "time": datetime.utcnow().isoformat()
    }

def log_signal(row):
    write_header = not os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(row)

def plot_performance():
    profits = []
    with open(LOG_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            profits.append(float(row["profit"]))
    cumulative = []
    s = 0
    for p in profits:
        s += p
        cumulative.append(s)
    plt.figure(figsize=(10,5))
    plt.plot(cumulative, label="Cumulative Profit", linewidth=2)
    plt.title("Forward Test Cumulative Profit")
    plt.xlabel("Step")
    plt.ylabel("Profit (USDT)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(CHART_FILE)
    print(f"✅ نمودار ذخیره شد: {CHART_FILE}")

def run_forward_test():
    ensure_dirs()
    print("🚀 شروع تست زنده سیگنال‌ها (pipeline-connected)...")
    for i in range(10):
        for symbol in SYMBOLS:
            price = fetch_price_usdt(symbol)
            #a فرض: df شامل priceهای قبلی نماد
            df = enrich_dataframe(df)
            row = df.iloc[-1]
            signal = decide_signal_from_indicators(row)
            if price:
                signal = generate_signal(symbol, price)
                log_signal(signal)
                print(f"[{signal['time']}] {symbol} → {signal['signal']} → {signal['result']} → Profit: {signal['profit']}")
        time.sleep(2)
    plot_performance()
    print("✅ تست زنده کامل شد.")

if __name__ == "__main__":
    run_forward_test()

