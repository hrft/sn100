import csv
import os

def save_signal_to_csv(signal, symbol, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"{symbol}_signal.csv")

    if isinstance(signal, dict):
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["key", "value"])
            for k, v in signal.items():
                writer.writerow([k, v])
    elif isinstance(signal, list):
        keys = signal[0].keys() if signal else []
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(signal)
    else:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(str(signal))
