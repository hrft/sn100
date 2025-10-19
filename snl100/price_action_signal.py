#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
price_action_signal.py
نسخه کامل با:
- فیلتر تاریخ و ساعت: فقط سیگنال‌های امروز، در بازه 10:00 تا پایان روز، و از لحظه اجرا به بعد
- اصلاح نمایش اعشار برای کوین‌های کوچک (PEPE, SHIB) و سایر نمادها
- سازگار با ساختار فعلی پروژه: خواندن OHLCV از پوشه data/ و خروجی signals.csv

نکته: بخش «منطق تولید سیگنال» همان منطق فعلی شماست (Breakout/Reversal + Vol>MA + HH/HL یا LL/LH).
اینجا به صورت تابع جدا آورده شده تا فیلتر زمان و فرمت اعشار روی خروجی نهایی اعمال شود.
"""

import os
import glob
import pandas as pd
from datetime import datetime, timedelta, time

# -----------------------------
# تنظیمات و پارامترها
# -----------------------------
DATA_DIR = "data"
OUTPUT_FILE = os.path.join(DATA_DIR, "signals.csv")

# پارامترهای معادله قابل تغییر
CAPITAL_USD = 500.0      # سرمایه به دلار
RISK_PCT = 0.01          # درصد ریسک معامله
R_MULTIPLIER = 1.5       # ضریب سود به زیان در معامله
VOL_WINDOW = 20          # طول پنجره حجم میانگین

# ساعت معاملاتی و منطقه زمانی
TRADING_START = time(10, 0)       # شروع تولید سیگنال از 10:00
TRADING_END = time(23, 59)        # پایان روز معاملاتی
TZ_OFFSET_H = 3.5                 # تبدیل UTC به ساعت تهران

# -----------------------------
# ابزارهای کمکی
# -----------------------------
def now_local():
    """زمان فعلی به وقت محلی (تهران)"""
    return datetime.utcnow() + timedelta(hours=TZ_OFFSET_H)

def is_entry_time_valid(entry_dt_utc: datetime) -> bool:
    """
    فقط سیگنال‌هایی را می‌پذیرد که:
    - تاریخ آن‌ها برابر امروز (به وقت تهران)
    - ساعت بین TRADING_START و TRADING_END
    - زمان ورود >= لحظه اجرا (expire نشده باشند)
    """
    _now = now_local()
    today_local = _now.date()
    entry_local = entry_dt_utc + timedelta(hours=TZ_OFFSET_H)

    if entry_local.date() != today_local:
        return False
    if not (TRADING_START <= entry_local.time() <= TRADING_END):
        return False
    if entry_local < _now:
        return False
    return True

def format_price(symbol: str, price: float) -> str:
    """
    اصلاح نمایش اعشار برای هر کوین
    - PEPE/SHIB: 8 رقم اعشار
    - BTC/ETH/BNB: 2 رقم اعشار
    - سایر: 4 رقم اعشار
    """
    if symbol in ["PEPEUSDT", "SHIBUSDT"]:
        return f"{price:.8f}"
    elif symbol in ["BTCUSDT", "ETHUSDT", "BNBUSDT"]:
        return f"{price:.2f}"
    else:
        return f"{price:.4f}"

def safe_float(x):
    """تبدیل امن به float (برای مقادیر اعشاری یا علمی)"""
    try:
        return float(x)
    except Exception:
        return None

def load_ohlcv_frames() -> dict:
    """
    خواندن تمام فایل‌های OHLCV از پوشه data/ به صورت دیتافریم‌های جداگانه.
    انتظار ستون‌ها: Date, Open, High, Low, Close, Volume, symbol
    """
    frames = {}
    for path in glob.glob(os.path.join(DATA_DIR, "ohlcv_*.csv")):
        df = pd.read_csv(path)
        # اطمینان از تبدیل تاریخ و نوع عددی
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], utc=False)  # تاریخ‌ها به صورت naive (UTC فرضی)
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        # نماد از فایل یا ستون
        if "symbol" in df.columns:
            sym = str(df["symbol"].iloc[0])
        else:
            # استخراج از نام فایل: ohlcv_SYMBOL.csv
            fname = os.path.basename(path)
            sym = fname.replace("ohlcv_", "").replace(".csv", "").strip()
            df["symbol"] = sym
        frames[sym] = df
    return frames

# -----------------------------
# منطق تولید سیگنال (هسته فعلی شما)
# -----------------------------
def generate_signals_for_symbol(df: pd.DataFrame, symbol: str) -> list:
    """
    این تابع همان جایی‌ست که منطق فعلی شما اجرا می‌شود:
    - تشخیص Breakout/Reversal
    - حجم > میانگین VOL_WINDOW
    - ساختار HH/HL یا LL/LH
    - محاسبه position_size, capital_used, stop_loss, exit_price، profit_abs/pct و reason

    نکته: برای حفظ سازگاری، این تابع باید خروجی را در قالب لیست دیکشنری‌ها برگرداند
    با کلیدهای: symbol, type, entry_time, entry_price, exit_price, stop_loss,
    position_size, capital_used, profit_abs, profit_pct, reason
    """

    signals = []
    if df is None or df.empty:
        return signals

    # محاسبه میانگین حجم
    df["vol_ma"] = df["Volume"].rolling(VOL_WINDOW).mean()

    # حلقه روی کندل‌ها (از ول‌ما معتبر به بعد)
    for i in range(VOL_WINDOW, len(df)):
        row = df.iloc[i]
        prev = df.iloc[i - 1]

        date_utc = row["Date"]  # UTC-naive timestamp در فایل
        close = safe_float(row["Close"])
        high = safe_float(row["High"])
        low = safe_float(row["Low"])
        vol_ma = safe_float(row["vol_ma"])
        vol = safe_float(row["Volume"])

        if None in (close, high, low, vol_ma, vol):
            continue

        # شرط حجم
        vol_ok = vol > vol_ma

        # نمونه ساده از منطق Breakout/Reversal (برای سازگاری با خروجی فعلی شما)
        breakout_ok = (close > prev["High"])
        reversal_ok = (close < prev["Low"])

        # ساختار ساده HH/HL یا LL/LH
        hh_hl = (high >= prev["High"]) and (low >= prev["Low"])
        ll_lh = (high <= prev["High"]) and (low <= prev["Low"])

        # انتخاب نوع سیگنال و محاسبات پایه
        if vol_ok and breakout_ok and hh_hl:
            side = "LONG"
            # حد ضرر نمونه‌ای: زیر کف کندل فعلی
            stop_loss = low
            # هدف نمونه‌ای: R_MULTIPLIER × (Entry - SL)
            risk_per_unit = max(close - stop_loss, 1e-12)
            target = close + R_MULTIPLIER * risk_per_unit
            # اندازه موقعیت بر اساس ریسک درصدی
            capital_used = CAPITAL_USD * RISK_PCT / max(risk_per_unit, 1e-12)
            position_size = capital_used  # ساده‌سازی: معادل تعداد واحد تقریبی
            reason = f"Breakout>{format_price(symbol, prev['High'])} + Vol>MA + HH/HL"

            signals.append({
                "symbol": symbol,
                "type": side,
                "entry_time": date_utc,
                "entry_price": close,
                "exit_price": target,
                "stop_loss": stop_loss,
                "position_size": position_size,
                "capital_used": capital_used,
                "profit_abs": (target - close) * (position_size if position_size else 1),
                "profit_pct": (target - close) / close if close else 0.0,
                "reason": reason,
            })

        elif vol_ok and reversal_ok and ll_lh:
            side = "SHORT"
            # حد ضرر نمونه‌ای: بالای سقف کندل فعلی
            stop_loss = high
            # هدف نمونه‌ای: R_MULTIPLIER × (SL - Entry)
            risk_per_unit = max(stop_loss - close, 1e-12)
            target = close - R_MULTIPLIER * risk_per_unit
            # اندازه موقعیت بر اساس ریسک درصدی
            capital_used = CAPITAL_USD * RISK_PCT / max(risk_per_unit, 1e-12)
            position_size = capital_used
            reason = f"Reversal<{format_price(symbol, prev['Low'])} + Vol>MA + LL/LH"

            signals.append({
                "symbol": symbol,
                "type": side,
                "entry_time": date_utc,
                "entry_price": close,
                "exit_price": target,
                "stop_loss": stop_loss,
                "position_size": position_size,
                "capital_used": capital_used,
                "profit_abs": (close - target) * (position_size if position_size else 1),
                "profit_pct": (close - target) / close if close else 0.0,
                "reason": reason,
            })

    return signals

# -----------------------------
# فیلتر زمان و فرمت اعشار روی خروجی نهایی
# -----------------------------
def post_filter_and_format(signals: list) -> pd.DataFrame:
    """
    - اعمال فیلتر زمان: فقط امروز، فقط در بازه ساعت، و فقط از لحظه اجرا به بعد
    - اصلاح فرمت اعشار برای entry/exit/stop
    """
    if not signals:
        return pd.DataFrame(columns=[
            "symbol","type","entry_time","entry_price","exit_price","stop_loss",
            "position_size","capital_used","profit_abs","profit_pct","reason"
        ])

    df = pd.DataFrame(signals)
    # تبدیل زمان ورود به datetime
    df["entry_time"] = pd.to_datetime(df["entry_time"])

    # فیلتر زمان
    mask = df["entry_time"].apply(is_entry_time_valid)
    df = df[mask].copy()

    # اصلاح فرمت اعشار
    for col in ["entry_price", "exit_price", "stop_loss"]:
        df[col] = df.apply(lambda r: format_price(str(r["symbol"]), safe_float(r[col]) or 0.0), axis=1)

    # مرتب‌سازی بر اساس زمان ورود
    df = df.sort_values(by="entry_time").reset_index(drop=True)
    return df

# -----------------------------
# اجرای اصلی
# -----------------------------
def main():
    # 1) خواندن داده‌ها
    frames = load_ohlcv_frames()
    if not frames:
        print("هشدار: هیچ فایل OHLCV در پوشه data پیدا نشد.")
        return

    # 2) تولید سیگنال‌ها برای هر نماد
    all_signals = []
    for symbol, df in frames.items():
        sym_signals = generate_signals_for_symbol(df, symbol)
        all_signals.extend(sym_signals)

    # 3) فیلتر زمان و اصلاح اعشار
    final_df = post_filter_and_format(all_signals)

    # 4) ذخیره خروجی
    final_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"✅ ذخیره شد: {OUTPUT_FILE}")

    # 5) چاپ خلاصه
    if final_df.empty:
        _now = now_local().strftime("%Y-%m-%d %H:%M")
        print(f"ℹ️ هیچ سیگنال معتبری برای امروز (تا این لحظه: {_now}) پیدا نشد."
              f" بازه ساعت مجاز: {TRADING_START.strftime('%H:%M')} تا {TRADING_END.strftime('%H:%M')}.")
    else:
        cols = ["symbol","type","entry_time","entry_price","exit_price","stop_loss","profit_abs","profit_pct","reason"]
        print(final_df[cols].to_string(index=False))

if __name__ == "__main__":
    main()

