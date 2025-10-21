import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

plt.style.use("seaborn-v0_8")

st.set_page_config(page_title="SNL100 Dashboard", layout="wide")
st.title("📊 داشبورد مقایسه استراتژی‌ها (SNL100)")

# انتخاب نسخه استراتژی
strategy_file = st.selectbox(
    "انتخاب نسخه‌ی استراتژی:",
    options=["signals.csv", "signals_simple.csv"],
    format_func=lambda x: "نسخه‌ی اصلی (HH/HL, LL/LH)" if x == "signals.csv" else "نسخه‌ی ساده (Breakout/Reversal)"
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
data_path = os.path.join(DATA_DIR, strategy_file)

if not os.path.exists(data_path):
    st.error("فایل انتخاب‌شده وجود ندارد. اول price_action_signal.py را اجرا کن.")
    st.stop()

df = pd.read_csv(data_path)
if df.empty:
    st.warning("هیچ سیگنالی در این نسخه یافت نشد.")
    st.stop()

# تبدیل تاریخ
df["entry_date"] = pd.to_datetime(df["entry_date"])

# نمودار تعداد سیگنال‌ها بر اساس نماد
st.subheader("📈 تعداد سیگنال‌ها بر اساس نماد")
symbol_counts = df["symbol"].value_counts()
st.bar_chart(symbol_counts)

# نمودار تعداد سیگنال‌ها بر اساس تاریخ
st.subheader("📈 تعداد سیگنال‌ها بر اساس تاریخ")
date_counts = df["entry_date"].dt.date.value_counts().sort_index()
st.line_chart(date_counts)

# محاسبه سود/زیان فرضی
st.subheader("💰 توزیع سود/زیان فرضی")
df["profit_abs"] = df.apply(
    lambda row: (row["exit_price"] - row["entry_price"]) if row["type"] == "LONG"
    else (row["entry_price"] - row["exit_price"]), axis=1
)
df["profit_pct"] = df["profit_abs"] / df["entry_price"] * 100
st.hist_chart(df["profit_pct"], bins=30)

# جدول سیگنال‌ها
st.subheader("📋 جدول سیگنال‌ها")
st.dataframe(df[[
    "symbol", "type", "entry_date", "entry_hour",
    "entry_price", "exit_price", "stop_loss", "profit_pct", "reason"
]], use_container_width=True)

