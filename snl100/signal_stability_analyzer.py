import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

INPUT_FILE = "output/forward_test_log.csv"
OUTPUT_DIR = "output/stability"
SUMMARY_FILE = os.path.join(OUTPUT_DIR, "summary.csv")

def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_data():
    df = pd.read_csv(INPUT_FILE)
    df["time"] = pd.to_datetime(df["time"])
    df["date"] = df["time"].dt.date
    df["strategy"] = df.get("strategy", "default")
    return df

def compute_metrics(group):
    profits = group["profit"]
    hits = group["result"] == "hit_target"
    total = len(group)
    hit_rate = hits.sum() / total if total else 0
    avg_profit = profits.mean()
    pos = profits[profits > 0].sum()
    neg = -profits[profits < 0].sum()
    profit_factor = pos / neg if neg > 0 else float("inf")
    cum = profits.cumsum()
    drawdown = (cum.cummax() - cum).max()
    sharpe = profits.mean() / profits.std() if profits.std() > 0 else 0
    return {
        "Total": total,
        "Hit Rate": round(hit_rate * 100, 2),
        "Avg Profit": round(avg_profit, 4),
        "Profit Factor": round(profit_factor, 2),
        "Max Drawdown": round(drawdown, 4),
        "Sharpe Ratio": round(sharpe, 2)
    }

def analyze(df):
    summary = []
    for (strategy, date), group in df.groupby(["strategy", "date"]):
        metrics = compute_metrics(group)
        metrics["Strategy"] = strategy
        metrics["Date"] = date
        summary.append(metrics)
    return pd.DataFrame(summary)

def plot_metric(df, metric):
    for strategy in df["Strategy"].unique():
        subset = df[df["Strategy"] == strategy]
        plt.figure(figsize=(10,5))
        plt.plot(subset["Date"], subset[metric], marker="o")
        plt.title(f"{metric} - {strategy}")
        plt.xlabel("Date")
        plt.ylabel(metric)
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        path = os.path.join(OUTPUT_DIR, f"{strategy}_{metric.lower().replace(' ', '_')}.png")
        plt.savefig(path)
        plt.close()

def run():
    ensure_dirs()
    df = load_data()
    summary = analyze(df)
    summary.to_csv(SUMMARY_FILE, index=False)
    print(f"✅ ذخیره شد: {SUMMARY_FILE}")
    for metric in ["Hit Rate", "Avg Profit", "Profit Factor", "Max Drawdown", "Sharpe Ratio"]:
        plot_metric(summary, metric)

if __name__ == "__main__":
    run()

