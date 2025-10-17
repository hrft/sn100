# snl100/price_action_signal.py

import csv
from datetime import datetime
from statistics import mean

INPUT_FILE = "data/ohlcv.csv"
OUTPUT_FILE = "output/price_action_log.csv"

def load_data(path):
    data = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                data.append({
                    "timestamp": datetime.fromisoformat(row["timestamp"]),
                    "symbol": row["symbol"],
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": float(row["volume"])
                })
            except:
                continue
    return data

def detect_zone(data, i):
    # بررسی سقف/کف در 5 کندل اخیر
    window = data[max(0, i-5):i+1]
    highs = [row["high"] for row in window]
    lows = [row["low"] for row in window]
    if data[i]["low"] == min(lows):
        return "demand"
    elif data[i]["high"] == max(highs):
        return "supply"
    return None

def detect_pattern(data, i):
    # Engulfing, Hammer, Doji
    candle = data[i]
    body = abs(candle["close"] - candle["open"])
    range_ = candle["high"] - candle["low"]
    if body < 0.2 * range_:
        return "doji"
    elif candle["close"] > candle["open"] and body > 0.6 * range_:
        prev = data[i-1]
        if candle["open"] < prev["close"] and candle["close"] > prev["open"]:
            return "bullish_engulfing"
    elif candle["close"] < candle["open"] and body > 0.6 * range_:
        prev = data[i-1]
        if candle["open"] > prev["close"] and candle["close"] < prev["open"]:
            return "bearish_engulfing"
    return None

def check_volume(data, i):
    # حجم بالاتر از میانگین 10 کندل اخیر
    volumes = [row["volume"] for row in data[max(0, i-10):i]]
    avg_vol = mean(volumes) if volumes else 0
    return data[i]["volume"] > 1.2 * avg_vol

def validate_trend(data, i):
    # بررسی HH/HL یا LH/LL
    if i < 3:
        return None
    h1, h2, h3 = data[i-3]["high"], data[i-2]["high"], data[i-1]["high"]
    l1, l2, l3 = data[i-3]["low"], data[i-2]["low"], data[i-1]["low"]
    if h1 < h2 < h3 and l1 < l2 < l3:
        return "uptrend"
    elif h1 > h2 > h3 and l1 > l2 > l3:
        return "downtrend"
    return None

def filter_by_time(ts):
    return 9 <= ts.hour <= 15

def generate_signals(data):
    signals = []
    for i in range(5, len(data)):
        ts = data[i]["timestamp"]
        if not filter_by_time(ts):
            continue
        zone = detect_zone(data, i)
        pattern = detect_pattern(data, i)
        volume_ok = check_volume(data, i)
        trend = validate_trend(data, i)

        confidence = "LOW"
        if zone and pattern and volume_ok and trend:
            confidence = "HIGH"
        elif zone and pattern:
            confidence = "MEDIUM"

        if confidence != "LOW":
            signals.append({
                "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
                "symbol": data[i]["symbol"],
                "zone": zone,
                "pattern": pattern,
                "volume": round(data[i]["volume"], 2),
                "trend": trend,
                "signal": "BUY" if zone == "demand" else "SELL",
                "confidence": confidence
            })
    return signals

def save_signals(signals, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(signals[0].keys()))
        writer.writeheader()
        for s in signals:
            writer.writerow(s)

def main():
    data = load_data(INPUT_FILE)
    signals = generate_signals(data)
    if signals:
        save_signals(signals, OUTPUT_FILE)
        print(f"✅ {len(signals)} سیگنال ذخیره شد در {OUTPUT_FILE}")
    else:
        print("⚠️ هیچ سیگنالی یافت نشد.")

if __name__ == "__main__":
    main()

