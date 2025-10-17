import csv
import os
import math
from collections import defaultdict, Counter
from statistics import mean, pstdev
from datetime import datetime

# Optional plotting (robust: skips if not available)
HAS_PLOT = True
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
except Exception:
    HAS_PLOT = False

LOG_FILE = "output/forward_test_log.csv"
OUT_DIR = "output"


def ensure_outdir():
    os.makedirs(OUT_DIR, exist_ok=True)


def parse_row(row):
    """
    Expected keys: timestamp, symbol, strategy, profit
    Robust parsing: skips invalid rows.
    """
    try:
        ts_raw = row.get("timestamp", "").strip()
        symbol = row.get("symbol", "").strip()
        strategy = row.get("strategy", "").strip()
        profit = float(row.get("profit", ""))
        # Parse timestamp -> datetime
        ts = None
        if ts_raw:
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y/%m/%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S.%fZ"):
                try:
                    ts = datetime.strptime(ts_raw, fmt)
                    break
                except Exception:
                    continue
            # Fallback: try fromisoformat (Python 3.7+)
            if ts is None:
                try:
                    ts = datetime.fromisoformat(ts_raw.replace("Z", ""))
                except Exception:
                    ts = None
        return {
            "timestamp": ts,
            "symbol": symbol,
            "strategy": strategy,
            "profit": profit
        }
    except Exception:
        return None


def load_signals(path=LOG_FILE):
    data = []
    if not os.path.exists(path):
        raise FileNotFoundError(f"Log file not found: {path}")
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            parsed = parse_row(row)
            if parsed and parsed["strategy"] and parsed["symbol"]:
                data.append(parsed)
    return data


def safe_mean(values):
    return mean(values) if values else 0.0


def safe_pstdev(values):
    if not values:
        return 0.0
    if len(values) == 1:
        return 0.0
    return pstdev(values)


def sharpe_like(avg, std):
    # Avoid division by zero; not annualized; indicative only.
    if std == 0:
        return float("inf") if avg > 0 else 0.0
    return avg / std


def summarize_by_strategy(data):
    buckets = defaultdict(list)
    for d in data:
        buckets[d["strategy"]].append(d["profit"])

    summary = []
    for strat, profits in buckets.items():
        cnt = len(profits)
        total = round(sum(profits), 6)
        avg = round(safe_mean(profits), 6)
        std = safe_pstdev(profits)
        success = len([p for p in profits if p > 0])
        success_rate = round(100.0 * success / cnt, 2) if cnt else 0.0
        sharpe = round(sharpe_like(avg, std), 6)
        summary.append({
            "strategy": strat,
            "signals": cnt,
            "total_profit": total,
            "avg_profit": avg,
            "std_profit": round(std, 6),
            "success_rate_pct": success_rate,
            "sharpe_like": sharpe
        })
    # Sort by total_profit desc
    summary.sort(key=lambda x: x["total_profit"], reverse=True)
    return summary


def save_csv(path, rows, headers):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def plot_histograms_by_strategy(data):
    if not HAS_PLOT:
        return
    # Collect profits per strategy
    buckets = defaultdict(list)
    for d in data:
        buckets[d["strategy"]].append(d["profit"])
    for strat, profits in buckets.items():
        if not profits:
            continue
        plt.figure(figsize=(7, 4))
        sns.histplot(profits, bins=min(30, max(10, int(math.sqrt(len(profits))))) , kde=True, color="#3b82f6")
        plt.title(f"Profit distribution — {strat}")
        plt.xlabel("Profit")
        plt.ylabel("Frequency")
        plt.tight_layout()
        out_path = os.path.join(OUT_DIR, f"hist_strategy_{sanitize_name(strat)}.png")
        plt.savefig(out_path)
        plt.close()


def sanitize_name(name):
    return "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in name)


def analyze_by_hour(data):
    # hour -> [profits]
    hourly = defaultdict(list)
    for d in data:
        ts = d["timestamp"]
        if ts is None:
            continue
        hourly[ts.hour].append(d["profit"])
    rows = []
    for h in range(24):
        profits = hourly.get(h, [])
        cnt = len(profits)
        total = round(sum(profits), 6)
        avg = round(safe_mean(profits), 6)
        std = round(safe_pstdev(profits), 6)
        success = len([p for p in profits if p > 0])
        sr = round(100.0 * success / cnt, 2) if cnt else 0.0
        rows.append({
            "hour": h,
            "signals": cnt,
            "total_profit": total,
            "avg_profit": avg,
            "std_profit": std,
            "success_rate_pct": sr
        })
    # Optional heatmap
    if HAS_PLOT:
        try:
            # Build matrix 24 x 1 for avg profit; then show as heatmap-like bar
            hours = [r["hour"] for r in rows]
            avgs = [r["avg_profit"] for r in rows]
            plt.figure(figsize=(10, 3))
            sns.barplot(x=hours, y=avgs, color="#10b981")
            plt.title("Average profit by hour-of-day")
            plt.xlabel("Hour")
            plt.ylabel("Avg profit")
            plt.tight_layout()
            plt.savefig(os.path.join(OUT_DIR, "hourly_heatmap.png"))
            plt.close()
        except Exception:
            pass
    return rows


def pivot_strategy_symbol(data):
    # Build: (strategy, symbol) -> profits list
    grid = defaultdict(list)
    for d in data:
        grid[(d["strategy"], d["symbol"])].append(d["profit"])

    rows = []
    for (strat, sym), profits in grid.items():
        cnt = len(profits)
        total = round(sum(profits), 6)
        avg = round(safe_mean(profits), 6)
        std = round(safe_pstdev(profits), 6)
        success = len([p for p in profits if p > 0])
        sr = round(100.0 * success / cnt, 2) if cnt else 0.0
        rows.append({
            "strategy": strat,
            "symbol": sym,
            "signals": cnt,
            "total_profit": total,
            "avg_profit": avg,
            "std_profit": std,
            "success_rate_pct": sr
        })
    # Sort: strategy, then total_profit desc
    rows.sort(key=lambda x: (x["strategy"], -x["total_profit"], x["symbol"]))
    return rows


def main():
    ensure_outdir()
    data = load_signals(LOG_FILE)
    if not data:
        print("No valid rows found in log. Ensure output/forward_test_log.csv has columns: timestamp,symbol,strategy,profit")
        return

    # 1) Summary per strategy
    summary = summarize_by_strategy(data)
    save_csv(os.path.join(OUT_DIR, "strategy_summary.csv"), summary, headers=[
        "strategy", "signals", "total_profit", "avg_profit", "std_profit", "success_rate_pct", "sharpe_like"
    ])
    print("Saved: output/strategy_summary.csv")

    # 2) Distribution plots per strategy
    plot_histograms_by_strategy(data)
    if HAS_PLOT:
        print("Saved: output/hist_strategy_<strategy>.png (per strategy distributions)")
    else:
        print("Plotting libraries not available; distributions skipped.")

    # 3) Hour-of-day analysis
    hourly_rows = analyze_by_hour(data)
    save_csv(os.path.join(OUT_DIR, "strategy_hourly.csv"), hourly_rows, headers=[
        "hour", "signals", "total_profit", "avg_profit", "std_profit", "success_rate_pct"
    ])
    print("Saved: output/strategy_hourly.csv")
    if HAS_PLOT:
        print("Saved: output/hourly_heatmap.png")

    # 4) Strategy × symbol pivot
    pivot_rows = pivot_strategy_symbol(data)
    save_csv(os.path.join(OUT_DIR, "strategy_symbol_pivot.csv"), pivot_rows, headers=[
        "strategy", "symbol", "signals", "total_profit", "avg_profit", "std_profit", "success_rate_pct"
    ])
    print("Saved: output/strategy_symbol_pivot.csv")

    # Quick console highlights
    print("\nTop strategies by total_profit:")
    for s in summary[:5]:
        print(f"- {s['strategy']} | total: {s['total_profit']} | avg: {s['avg_profit']} | SR: {s['success_rate_pct']}% | sharpe_like: {s['sharpe_like']}")


if __name__ == "__main__":
    main()

