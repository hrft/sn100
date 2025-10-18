# snl100/price_action_signal.py
import os
import glob
import pandas as pd
from datetime import time, timedelta

# تنظیمات فایل‌ها
DATA_DIR = "data"
OUTPUT_FILE = os.path.join(DATA_DIR, "signals.csv")

# پارامترهای معاملاتی (قابل تغییر)
CAPITAL_USD    = 500.0   # سرمایه پایه (دلاری)
RISK_PCT       = 0.01     # درصد ریسک هر معامله (1% از سرمایه)
RR_MULTIPLIER  = 1.5      # نسبت ریسک به ریوارد هدف
VOL_WINDOW     = 20       # میانگین حجمی برای تایید
TRADING_START  = time(9, 0)
TRADING_END    = time(15, 0)
TZ_OFFSET_H    = 3.5        # در صورت نیاز، تنظیم به ساعت تهران (مثلاً 3 یا 3.5)

def in_trading_hours(dt):
    local_dt = dt + timedelta(hours=TZ_OFFSET_H)
    return TRADING_START <= local_dt.time() <= TRADING_END

def previous_day_levels(df):
    df["date_only"] = df["Date"].dt.date
    unique_days = sorted(df["date_only"].unique())
    if len(unique_days) < 2:
        return None, None
    prev_day = unique_days[-2]
    prev_df = df[df["date_only"] == prev_day]
    if prev_df.empty:
        return None, None
    return prev_df["High"].max(), prev_df["Low"].min()

def position_sizing(entry_price, stop_loss, side):
    """محاسبه اندازه موقعیت بر اساس ریسک ثابت دلاری."""
    risk_dollar = CAPITAL_USD * RISK_PCT
    if side == "LONG":
        risk_per_unit = entry_price - stop_loss
    else:  # SHORT
        risk_per_unit = stop_loss - entry_price
    if risk_per_unit <= 0:
        return 0.0, 0.0
    size_units = risk_dollar / risk_per_unit
    capital_used = size_units * entry_price
    return size_units, capital_used

def detect_signals(df, symbol):
    signals = []
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    df["vol_ma"] = df["Volume"].rolling(VOL_WINDOW, min_periods=1).mean()

    day_high, day_low = previous_day_levels(df)
    if day_high is None or day_low is None:
        return signals

    for i in range(2, len(df)):
        row   = df.iloc[i]
        prev  = df.iloc[i - 1]

        if not in_trading_hours(row["Date"]):
            continue

        hh_hl = (row["High"] > prev["High"]) and (row["Low"] > prev["Low"])   # صعودی
        ll_lh = (row["High"] < prev["High"]) and (row["Low"] < prev["Low"])   # نزولی
        breakout_long  = (row["Close"] > day_high) and (row["Volume"] > row["vol_ma"])
        reversal_short = (row["Close"] < day_low)  and (row["Volume"] > row["vol_ma"])

        # لانگ
        if breakout_long and hh_hl:
            entry_price = float(row["Close"])
            stop_loss   = float(row["Low"])
            risk        = entry_price - stop_loss
            if risk <= 0:
                continue
            exit_price  = entry_price + RR_MULTIPLIER * risk
            size_units, capital_used = position_sizing(entry_price, stop_loss, "LONG")
            profit_abs = (exit_price - entry_price) * size_units
            profit_pct = (exit_price - entry_price) / entry_price * 100.0

            signals.append({
                "symbol": symbol,
                "type": "LONG",
                "entry_time": row["Date"],
                "entry_price": round(entry_price, 6),
                "exit_price": round(exit_price, 6),
                "stop_loss": round(stop_loss, 6),
                "position_size": round(size_units, 6),
                "capital_used": round(capital_used, 2),
                "profit_abs": round(profit_abs, 2),
                "profit_pct": round(profit_pct, 4),
                "reason": f"Breakout>{round(day_high,6)} + Vol>{VOL_WINDOW}MA + HH/HL"
            })

        # شورت
        if reversal_short and ll_lh:
            entry_price = float(row["Close"])
            stop_loss   = float(row["High"])
            risk        = stop_loss - entry_price
            if risk <= 0:
                continue
            exit_price  = entry_price - RR_MULTIPLIER * risk
            size_units, capital_used = position_sizing(entry_price, stop_loss, "SHORT")
            profit_abs = (entry_price - exit_price) * size_units
            profit_pct = (entry_price - exit_price) / entry_price * 100.0

            signals.append({
                "symbol": symbol,
                "type": "SHORT",
                "entry_time": row["Date"],
                "entry_price": round(entry_price, 6),
                "exit_price": round(exit_price, 6),
                "stop_loss": round(stop_loss, 6),
                "position_size": round(size_units, 6),
                "capital_used": round(capital_used, 2),
                "profit_abs": round(profit_abs, 2),
                "profit_pct": round(profit_pct, 4),
                "reason": f"Reversal<{round(day_low,6)} + Vol>{VOL_WINDOW}MA + LL/LH"
            })

    return signals

def main():
    paths = glob.glob(os.path.join(DATA_DIR, "ohlcv_*.csv")) + \
            glob.glob(os.path.join(DATA_DIR, "OHLCV_*.csv"))

    all_signals = []
    for path in sorted(paths):
        symbol = os.path.basename(path).split("_")[-1].replace(".csv", "")
        try:
            df = pd.read_csv(path, parse_dates=["Date"])
        except Exception:
            df = pd.read_csv(path)
            df["Date"] = pd.to_datetime(df["Date"])

        for col in ["Open", "High", "Low", "Close", "Volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=["Date", "Open", "High", "Low", "Close", "Volume"])

        signals = detect_signals(df, symbol)
        all_signals.extend(signals)

    signals_df = pd.DataFrame(all_signals)
    if not signals_df.empty:
        signals_df["entry_time"] = pd.to_datetime(signals_df["entry_time"])
        signals_df.sort_values(["entry_time", "symbol"], inplace=True)
        os.makedirs(DATA_DIR, exist_ok=True)
        signals_df.to_csv(OUTPUT_FILE, index=False)

        summary = signals_df[["symbol", "type", "entry_time", "entry_price", "exit_price", "stop_loss", "position_size", "profit_abs", "profit_pct"]].to_dict(orient="records")
        print("Signals:")
        for s in summary:
            print(s)
        print(f"\n✅ ذخیره شد: {OUTPUT_FILE}")
    else:
        print("⚠️ هیچ سیگنالی مطابق قواعد تولید نشد. پارامترها یا بازه زمانی را تنظیم کن.")

if __name__ == "__main__":
    main()

