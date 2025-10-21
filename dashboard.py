#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import os

# -----------------------------
# بارگذاری داده‌ها
# -----------------------------
@st.cache_data
def load_signals():
    try:
        df = pd.read_csv("data/signals.csv")
    except FileNotFoundError:
        return pd.DataFrame()

    # تبدیل ستون زمان به datetime
    if "entry_time" in df.columns:
        df["entry_time"] = pd.to_datetime(df["entry_time"], errors="coerce")
        df = df.dropna(subset=["entry_time"])

    # تبدیل ستون‌های عددی به float
    numeric_cols = ["entry_price", "exit_price", "stop_loss",
                    "profit_abs", "profit_pct", "position_size", "capital_used"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

# -----------------------------
# تابع رسم نمودار
# -----------------------------
def plot_signals(df, signal_type: str, deterministic_metric: str = None):
    if df.empty:
        return go.Figure()

    # حذف NaN در ستون انتخابی
    df = df.dropna(subset=[signal_type, "entry_time"])

    fig = go.Figure()

    # نمودار اصلی
    fig.add_trace(go.Scatter(
        x=df["entry_time"],
        y=df[signal_type],
        mode="lines+markers",
        name=signal_type
    ))

    # اگر متریک اضافی انتخاب شده باشد
    if deterministic_metric and deterministic_metric in df.columns:
        df = df.dropna(subset=[deterministic_metric])
        fig.add_trace(go.Scatter(
            x=df["entry_time"],
            y=df[deterministic_metric],
            mode="lines",
            name=deterministic_metric,
            line=dict(dash="dot")
        ))

    fig.update_layout(
        title="نمودار سیگنال‌ها",
        xaxis_title="زمان ورود",
        yaxis_title=signal_type,
        template="plotly_dark"
    )
    return fig

# -----------------------------
# گزارش روزانه
# -----------------------------
def daily_report(df):
    if df.empty:
        return "هیچ سیگنالی برای امروز وجود ندارد."

    today = pd.Timestamp.now().date()
    df_today = df[df["entry_time"].dt.date == today]

    if df_today.empty:
        return "هیچ سیگنالی برای امروز وجود ندارد."

    total = len(df_today)
    longs = len(df_today[df_today["type"] == "LONG"])
    shorts = len(df_today[df_today["type"] == "SHORT"])
    avg_profit = df_today["profit_pct"].mean() * 100 if "profit_pct" in df_today else 0

    report = f"""
    📅 گزارش روزانه ({today}):
    - تعداد کل سیگنال‌ها: {total}
    - LONG: {longs} | SHORT: {shorts}
    - میانگین سود پیش‌بینی‌شده: {avg_profit:.2f}٪
    """
    return report

# -----------------------------
# رابط کاربری Streamlit
# -----------------------------

st.set_page_config(page_title="snl100 داشبورد سیگنال", layout="wide")
st.title("📊 snl100 داشبورد سیگنال")
st.subheader("گزارش روزانه")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SIGNAL_FILE = os.path.join(DATA_DIR, "signals.csv")

if not os.path.exists(SIGNAL_FILE):
    st.warning("⚠️ فایل سیگنال‌ها پیدا نشد.")
    st.stop()

df = pd.read_csv(SIGNAL_FILE)

if "entry_date" not in df.columns or "entry_hour" not in df.columns:
    st.error("❌ ستون‌های entry_date و entry_hour در فایل موجود نیستند.")
    st.stop()

df["entry_datetime"] = pd.to_datetime(df["entry_date"] + " " + df["entry_hour"], errors="coerce")
df = df.sort_values(by="entry_datetime", ascending=False)

cols = [
    "symbol","type","entry_date","entry_hour",
    "entry_price","exit_price","stop_loss",
    "profit_abs","profit_pct","reason"
]

st.dataframe(df[cols], use_container_width=True)

st.markdown("### 📈 آمار کلی")
st.write(f"تعداد سیگنال‌ها: {len(df)}")
st.write(f"تعداد LONG: {len(df[df['type'] == 'LONG'])}")
st.write(f"تعداد SHORT: {len(df[df['type'] == 'SHORT'])}")
st.write(f"میانگین سود درصدی: {df['profit_pct'].astype(float).mean():.2%}")

