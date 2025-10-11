import os
import csv
from pathlib import Path
from datetime import datetime

def simulate_signal_execution(signal):
    try:
        entry = float(signal.get("Entry", 0))
        stop = float(signal.get("Stop", 0))
        target = float(signal.get("Target", 0))
    except Exception:
        return {"result": "invalid", "profit": 0}

    simulated_high = entry * 1.02
    simulated_low = entry * 0.98

    if simulated_high >= target:
        profit = round(target - entry, 4)
        return {"result": "hit_target", "profit": profit}
    elif simulated_low <= stop:
        loss = round(entry - stop, 4)
        return {"result": "hit_stop", "profit": -loss}
    else:
        return {"result": "neutral", "profit": 0}

def load_signals(output_dir="output"):
    signal_files = list(Path(output_dir).glob("*_signal.csv"))
    # signal_files = list(Path("output").glob("*_signal.csv"))

    signals = []

    for file in signal_files:
        try:
            with open(file, encoding="utf-8") as f:
                reader = csv.reader(f)
                lines = list(reader)
        except Exception as e:
            print(f"⚠️ خطا در خواندن {file}: {e}")
            continue

        if len(lines) > 0 and lines[0] == ["key", "value"]:
            data = dict(lines[1:])
            signals.append(data)
        elif len(lines) > 0 and "Symbol" in lines[0]:
            headers = lines[0]
            for line in lines[1:]:
                row = dict(zip(headers, line))
                signals.append(row)
        else:
            continue

    return signals

def save_results(results, output_dir="output", filename="results.csv"):
    keys = ["Time", "Symbol", "Entry", "Stop", "Target", "Result", "Profit"]
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in results:
            writer.writerow(r)

def run_simulation():
    print("🚀 تابع run_simulation وارد شد")
    signals = load_signals(output_dir="output")
    #print("\noutput_dir: ", output_dir, "\nSignals:",signals)
    results = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    for s in signals:
        symbol = s.get("Symbol", "UNKNOWN")
        sim = simulate_signal_execution(s)
        result = {
            "Time": s.get("Time", now),
            "Symbol": symbol,
            "Entry": s.get("Entry", ""),
            "Stop": s.get("Stop", ""),
            "Target": s.get("Target", ""),
            "Result": sim["result"],
            "Profit": sim["profit"]
        }
        results.append(result)
        print(f"🧪 {symbol}: {result['Result']} → سود: {result['Profit']}")

    save_results(results)
    print("✅ نتایج شبیه‌سازی ذخیره شد: output/results.csv")

if __name__ == "__main__":
    print("📦 اجرای اصلی شروع شد")
    run_simulation()

