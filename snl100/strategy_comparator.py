import os
import csv
import matplotlib.pyplot as plt

def read_results(file_path):
    profits = []
    hit_count = 0
    total = 0
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            profit = float(row.get("Profit", 0))
            result = row.get("Result", "")
            profits.append(profit)
            total += 1
            if result == "hit_target":
                hit_count += 1
    return profits, hit_count, total

def compare_strategies():
    v1_path = "output/results_v1.csv"
    v2b_path = "output/results_v2b.csv"
    if not os.path.exists(v1_path) or not os.path.exists(v2b_path):
        print("❌ یکی از فایل‌های نتایج وجود ندارد.")
        return

    v1_profits, v1_hits, v1_total = read_results(v1_path)
    v2b_profits, v2b_hits, v2b_total = read_results(v2b_path)

    v1_cumulative = [sum(v1_profits[:i+1]) for i in range(len(v1_profits))]
    v2b_cumulative = [sum(v2b_profits[:i+1]) for i in range(len(v2b_profits))]

    plt.figure(figsize=(10, 6))
    plt.plot(v1_cumulative, label="v1", linewidth=2)
    plt.plot(v2b_cumulative, label="v2b", linewidth=2)
    plt.title("📈 Cumulative Profit Comparison")
    plt.xlabel("Signal Index")
    plt.ylabel("Cumulative Profit")
    plt.legend()
    plt.grid(True)

    os.makedirs("output/comparison", exist_ok=True)
    chart_path = "output/comparison/strategy_comparison.png"
    plt.savefig(chart_path)
    print(f"✅ نمودار مقایسه‌ای ذخیره شد: {chart_path}")

    print("\n📊 خلاصه‌ی عملکرد:")
    print(f"v1:  Signals={v1_total}, Hit Target={v1_hits}, Success Rate={round(v1_hits/v1_total*100, 2)}%, Avg Profit={round(sum(v1_profits)/v1_total, 4)}")
    print(f"v2b: Signals={v2b_total}, Hit Target={v2b_hits}, Success Rate={round(v2b_hits/v2b_total*100, 2)}%, Avg Profit={round(sum(v2b_profits)/v2b_total, 4)}")

if __name__ == "__main__":
    compare_strategies()

