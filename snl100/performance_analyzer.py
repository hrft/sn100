import csv
from collections import defaultdict

def analyze_results(input_file="output/results.csv"):
    symbol_stats = defaultdict(lambda: {
        "total": 0,
        "hit_target": 0,
        "hit_stop": 0,
        "neutral": 0,
        "total_profit": 0.0
    })

    with open(input_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            symbol = row["Symbol"]
            result = row["Result"]
            profit = float(row["Profit"])

            symbol_stats[symbol]["total"] += 1
            symbol_stats[symbol][result] += 1
            symbol_stats[symbol]["total_profit"] += profit

    # ذخیره‌ی خروجی نمادها
    with open("output/symbol_summary.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Symbol", "total_signals", "hit_target", "hit_stop", "neutral", "avg_profit", "total_profit", "success_rate_%"])
        for symbol, stats in symbol_stats.items():
            total = stats["total"]
            hit_target = stats["hit_target"]
            hit_stop = stats["hit_stop"]
            neutral = stats["neutral"]
            total_profit = stats["total_profit"]
            avg_profit = round(total_profit / total, 4) if total else 0
            success_rate = round((hit_target / total) * 100, 2) if total else 0
            writer.writerow([symbol, total, hit_target, hit_stop, neutral, avg_profit, round(total_profit, 4), success_rate])

    # محاسبه‌ی آمار کلی
    total_signals = sum(stats["total"] for stats in symbol_stats.values())
    total_profit = sum(stats["total_profit"] for stats in symbol_stats.values())
    avg_profit = round(total_profit / total_signals, 4) if total_signals else 0
    total_hit_target = sum(stats["hit_target"] for stats in symbol_stats.values())
    success_rate = round((total_hit_target / total_signals) * 100, 2) if total_signals else 0

    with open("output/overall_summary.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Total Signals", "Overall Avg Profit", "Overall Total Profit", "Overall Success Rate (%)"])
        writer.writerow([total_signals, avg_profit, round(total_profit, 4), success_rate])

    print("✅ تحلیل عملکرد کامل شد. خروجی‌ها در output/symbol_summary.csv و output/overall_summary.csv ذخیره شدند.")

if __name__ == "__main__":
    analyze_results()

