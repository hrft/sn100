import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="SNL100 Strategy Comparison", layout="wide")
st.title("📊 مقایسه همزمان دو استراتژی (ساده vs اصلی)")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
FILE_SIMPLE = os.path.join(DATA_DIR, "signals_simple.csv")
FILE_MAIN = os.path.join(DATA_DIR, "signals.csv")

def load_signals(path, label):
    if os.path.exists(path):
        df = pd.read_csv(path)
        if not df.empty:
            df["strategy"] = label
            return df
    return pd.DataFrame()

df_simple = load_signals(FILE_SIMPLE, "ساده (Breakout/Reversal)")
df_main = load_signals(FILE_MAIN, "اصلی (HH/HL, LL/LH)")

df_all = pd.concat([df_simple, df_main], ignore_index=True)

if df_all.empty:
    st.error("هیچ سیگنالی در هیچ‌کدام از نسخه‌ها پیدا نشد.")
    st.stop()

# انتخاب استراتژی‌ها برای مقایسه
strategies = st.multiselect("انتخاب استراتژی‌ها", options=df_all["strategy"].unique(),
                            default=df_all["strategy"].unique())
df_filtered = df_all[df_all["strategy"].isin(strategies)]

# جدول سیگنال‌ها
st.subheader("📋 جدول سیگنال‌ها")
st.dataframe(df_filtered[[
    "strategy","symbol","type","entry_date","entry_hour",
    "entry_price","exit_price","stop_loss","reason"
]], use_container_width=True)

# نمودار تعداد سیگنال‌ها بر اساس نماد
st.subheader("📈 تعداد سیگنال‌ها بر اساس نماد")
st.bar_chart(df_filtered.groupby(["strategy","symbol"])["type"].count().unstack(fill_value=0))

# نمودار تعداد سیگنال‌ها بر اساس تاریخ
st.subheader("📈 تعداد سیگنال‌ها بر اساس تاریخ")
df_filtered["entry_date"] = pd.to_datetime(df_filtered["entry_date"])
st.line_chart(df_filtered.groupby(["strategy",df_filtered["entry_date"].dt.date])["type"].count().unstack(fill_value=0))

# محاسبه سود/زیان فرضی
st.subheader("💰 سود/زیان فرضی")
df_filtered["profit_abs"] = df_filtered.apply(
    lambda row: (row["exit_price"] - row["entry_price"]) if row["type"]=="LONG"
    else (row["entry_price"] - row["exit_price"]), axis=1
)
df_filtered["profit_pct"] = df_filtered["profit_abs"] / df_filtered["entry_price"] * 100
st.bar_chart(df_filtered.groupby("strategy")["profit_pct"].mean())

