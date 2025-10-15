import os
import pandas as pd
import matplotlib.pyplot as plt
from snl100.config import OUTPUT_LOG

CHART_FILE = "output/performance_chart.png"

def analyze_performance():
    if not os.path.exists(OUTPUT_LOG):
        print(f"❌ فایل لاگ پیدا نشد: {OUTPUT_LOG}")
        return

    df = pd.read_csv(OUTPUT_LOG)

    # اگر profit نبود، از تخمینی استفاده کن
    if "profit" in df.columns:
        df["profit_final"] = pd.to_numeric(df["profit"], errors="coerce").fillna(0.0)
    else:
        def _estimate(row):
            sig = str(row.get("signal","hold")).lower()
            price = row.get("price"); target = row.get("target"); size = row.get("position_size")
            try:
                price = float(price); target = float(target); size = float(size)
            except Exception:
                return 0.0
            if sig == "buy": return (target - price) * size
            if sig == "sell": return (price - target) * size
            return 0.0
        df["profit_final"] = df.apply(_estimate, axis=1)

    valid = df[df["signal"].isin(["buy","sell"])].copy()
    if valid.empty:
        print("⚠️ سیگنال خرید/فروش کافی در لاگ نیست.")
        return

    valid["cumulative_profit"] = valid["profit_final"].cumsum()
    total = len(valid)
    avg_profit = valid["profit_final"].mean()
    best = valid.loc[valid["profit_final"].idxmax()]
    worst = valid.loc[valid["profit_final"].idxmin()]

    print("📊 گزارش عملکرد (USDT)")
    print("-"*40)
    print(f"تعداد سیگنال‌ها: {total}")
    print(f"میانگین سود هر سیگنال: {avg_profit:.4f}")
    print(f"بهترین: {best['symbol']} {best['signal']} → {best['profit_final']:.4f} در {best['time']}")
    print(f"بدترین: {worst['symbol']} {worst['signal']} → {worst['profit_final']:.4f} در {worst['time']}")

    plt.figure(figsize=(10,5))
    plt.plot(valid["cumulative_profit"], label="Cumulative profit", linewidth=2)
    plt.title("Equity curve (USDT)")
    plt.xlabel("Signal index")
    plt.ylabel("Profit (USDT)")
    plt.grid(True); plt.legend(); plt.tight_layout()
    plt.savefig(CHART_FILE)
    print(f"✅ نمودار ذخیره شد: {CHART_FILE}")

if __name__ == "__main__":
    analyze_performance()

