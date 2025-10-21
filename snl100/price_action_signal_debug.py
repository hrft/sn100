#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
import glob

# -----------------------------
# تنظیمات
# -----------------------------
BASE_DIR = os.path.dirname(__file__)
# DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
VOL_WINDOW = 20   # میانگین متحرک حجم

# -----------------------------
# ابزارهای کمکی
# -----------------------------
def safe_float(x):
    try:
        return float(x)
    except Exception:
        return None

# -----------------------------
# بارگذاری داده‌ها
# -----------------------------
def load_ohlcv_frames():
    frames = {}
    for path in glob.glob(os.path.join(DATA_DIR, "ohlcv_*.csv")):
        df = pd.read_csv(path)
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], utc=False)

        # اطمینان از عددی بودن ستون‌ها
        for col in ["Open", "High", "Low", "Close", "VolumeFrom", "VolumeTo"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        sym = str(df["symbol"].iloc[0]) if "symbol" in df.columns else os.path.basename(path).replace("ohlcv_", "").replace(".csv", "")
        df["symbol"] = sym
        frames[sym] = df
    return frames

# -----------------------------
# تحلیل شرط‌ها
# -----------------------------
def analyze_conditions(df, symbol):
    if df is None or df.empty:
        return

    # استفاده از VolumeTo برای تحلیل
    df["vol_ma"] = df["VolumeTo"].rolling(VOL_WINDOW).mean()

    breakout_count = 0
    reversal_count = 0
    vol_ok_count = 0

    for i in range(VOL_WINDOW, len(df)):
        row = df.iloc[i]
        prev = df.iloc[i - 1]

        close = safe_float(row["Close"])
        high = safe_float(row["High"])
        low = safe_float(row["Low"])
        vol_ma = safe_float(row["vol_ma"])
        vol = safe_float(row["VolumeTo"])
        prev_high = safe_float(prev["High"])
        prev_low = safe_float(prev["Low"])

        if None in (close, high, low, vol_ma, vol, prev_high, prev_low):
            continue

        if close > prev_high:
            breakout_count += 1
        if close < prev_low:
            reversal_count += 1
        if vol > vol_ma:
            vol_ok_count += 1

    print(f"📊 {symbol}: Breakout={breakout_count}, Reversal={reversal_count}, Vol>MA={vol_ok_count}, Total={len(df)}")

# -----------------------------
# اجرای اصلی
# -----------------------------
if __name__ == "__main__":
    frames = load_ohlcv_frames()
    for symbol, df in frames.items():
        analyze_conditions(df, symbol)

