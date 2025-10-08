# Helper functions
import pandas as pd
import os
from datetime import datetime

def save_signal_to_csv(signal_data, symbol="BTCUSDT", output_dir="output/signals"):
    if signal_data["signal"] is None:
        print("⚠️ سیگنالی برای ذخیره وجود ندارد.")
        return

    os.makedirs(output_dir, exist_ok=True)

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    filename = f"{output_dir}/{symbol}_signal.csv"

    df = pd.DataFrame([{
        "time": now,
        "symbol": symbol,
        "signal": signal_data["signal"],
        "entry": signal_data["entry"],
        "stop": signal_data["stop"],
        "target": signal_data["target"]
    }])

    if os.path.exists(filename):
        df.to_csv(filename, mode="a", header=False, index=False)
    else:
        df.to_csv(filename, index=False)

    print(f"✅ سیگنال ذخیره شد: {filename}")

