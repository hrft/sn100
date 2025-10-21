#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
import pandas as pd

# -----------------------------
# تنظیمات
# -----------------------------
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "signals.csv")

os.makedirs(DATA_DIR, exist_ok=True)

CAPITAL_USD = 500.0
RISK_PCT = 0.01
R_MULTIPLIER = 1.5
VOL_WINDOW = 10   # ساده‌تر

# -----------------------------
# ابزارهای کمکی
# -----------------------------
def safe_float(x):
    try:
        return float(x)
    except Exception:
        return None

def load_ohlcv_frames() -> dict:
    frames = {}
    for path in glob.glob(os.path.join(DATA_DIR, "ohlcv_*.csv")):
        df = pd.read_csv(path)
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], utc=False)

        # استفاده از VolumeFrom
        if "VolumeFrom" in df.columns:
            df["Volume"] = pd.to_numeric(df["VolumeFrom"], errors="coerce")
        elif "Volume" in df.columns:
            df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce")
        else:
            continue

        for col in ["Open", "High", "Low", "Close"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        sym = str(df["symbol"].iloc[0]) if "symbol" in df.columns else os.path.basename(path).replace("ohlcv_", "").replace(".csv", "")
        df["symbol"] = sym
        frames[sym] = df
    return frames

# -----------------------------
# منطق تولید سیگنال مینیمال
# -----------------------------
def generate_signals_for_symbol(df: pd.DataFrame, symbol: str) -> list:
    signals = []
    if df is None or df.empty:
        return signals

    df["vol_ma"] = df["Volume"].rolling(VOL_WINDOW).mean()

    for i in range(VOL_WINDOW, len(df)):
        row = df.iloc[i]
        prev = df.iloc[i - 1]

        date_utc = row["Date"]
        close = safe_float(row["Close"])
        high = safe_float(row["High"])
        low = safe_float(row["Low"])
        vol_ma = safe_float(row["vol_ma"])
        vol = safe_float(row["Volume"])

        if None in (close, high, low, vol_ma, vol):
            continue

        vol_ok = vol > vol_ma
        breakout_ok = (close > prev["High"])
        reversal_ok = (close < prev["Low"])

        if vol_ok and breakout_ok:
            stop_loss = low
            risk_per_unit = max(close - stop_loss, 1e-12)
            target = close + R_MULTIPLIER * risk_per_unit
            capital_used = CAPITAL_USD * RISK_PCT / risk_per_unit
            signals.append({
                "symbol": symbol,
                "type": "LONG",
                "entry_time": date_utc,
                "entry_price": close,
                "exit_price": target,
                "stop_loss": stop_loss,
                "capital_used": capital_used,
                "reason": f"Breakout + Vol>MA"
            })

        elif vol_ok and reversal_ok:
            stop_loss = high
            risk_per_unit = max(stop_loss - close, 1e-12)
            target = close - R_MULTIPLIER * risk_per_unit
            capital_used = CAPITAL_USD * RISK_PCT / risk_per_unit
            signals.append({
                "symbol": symbol,
                "type": "SHORT",
                "entry_time": date_utc,
                "entry_price": close,
                "exit_price": target,
                "stop_loss": stop_loss,
                "capital_used": capital_used,
                "reason": f"Reversal + Vol>MA"
            })

    return signals

# -----------------------------
# اصلاح خروجی نهایی
# -----------------------------
def post_filter_and_format(signals: list) -> pd.DataFrame:
    if not signals:
        return pd.DataFrame(columns=[
            "symbol","type","entry_date","entry_hour","entry_price","exit_price","stop_loss","capital_used","reason"
        ])

    df = pd.DataFrame(signals)
    df["entry_time"] = pd.to_datetime(df["entry_time"])
    df["entry_date"] = df["entry_time"].dt.strftime("%Y-%m-%d")
    df["entry_hour"] = df["entry_time"].dt.strftime("%H:%M")
    df = df.sort_values(by="entry_time").reset_index(drop=True)
    df.drop(columns=["entry_time"], inplace=True)
    return df

# -----------------------------
# اجرای اصلی
# -----------------------------
if __name__ == "__main__":
    frames = load_ohlcv_frames()
    all_signals = []
    for symbol, df in frames.items():
        all_signals.extend(generate_signals_for_symbol(df, symbol))

    final_df = post_filter_and_format(all_signals)
    final_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"✅ ذخیره شد: {OUTPUT_FILE}")
    print(final_df.head())

