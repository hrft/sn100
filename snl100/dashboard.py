import streamlit as st
import pandas as pd
import os

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
SIGNALS_FILE = os.path.join(DATA_DIR, "signals.csv")

st.set_page_config(page_title="SNL100 Dashboard", layout="wide")

st.title("📊 داشبورد سیگنال‌های SNL100")

if not os.path.exists(SIGNALS_FILE):
    st.error("فایل signals.csv پیدا نشد! اول price_action_signal.py رو اجرا کن.")
else:
    df = pd.read_csv(SIGNALS_FILE)

    if df.empty:
        st.warning("هیچ سیگنالی پیدا نشد.")
    else:
        # فیلترها
        symbols = st.multiselect("انتخاب نماد", options=df["symbol"].unique(), default=df["symbol"].unique())
        types = st.multiselect("نوع سیگنال", options=df["type"].unique(), default=df["type"].unique())

        filtered = df[(df["symbol"].isin(symbols)) & (df["type"].isin(types))]

        st.subheader("📋 جدول سیگنال‌ها")
        st.dataframe(filtered, use_container_width=True)

        # نمودار تعداد سیگنال‌ها بر اساس نماد
        st.subheader("📈 تعداد سیگنال‌ها بر اساس نماد")
        st.bar_chart(filtered.groupby("symbol")["type"].count())

        # نمودار تعداد سیگنال‌ها بر اساس تاریخ
        st.subheader("📈 تعداد سیگنال‌ها بر اساس تاریخ")
        st.line_chart(filtered.groupby("entry_date")["type"].count())

        # نمودار سود/زیان فرضی
        if "entry_price" in filtered.columns and "exit_price" in filtered.columns:
            try:
                filtered["entry_price"] = pd.to_numeric(filtered["entry_price"], errors="coerce")
                filtered["exit_price"] = pd.to_numeric(filtered["exit_price"], errors="coerce")
                filtered["pnl"] = filtered["exit_price"] - filtered["entry_price"]
                st.subheader("💰 سود/زیان فرضی")
                st.bar_chart(filtered.groupby("symbol")["pnl"].sum())
            except Exception as e:
                st.warning(f"محاسبه سود/زیان ممکن نشد: {e}")

