import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="snl100 Dashboard", layout="wide")
st.title("📈 snl100 Signals Dashboard")

# بارگذاری داده‌ها
@st.cache_data
def load_data():
    df = pd.read_csv("data/signals.csv", parse_dates=["entry_time"])
    df["entry_time"] = pd.to_datetime(df["entry_time"])
    return df

df = load_data()

# فیلترها
symbols = sorted(df["symbol"].unique())
symbol = st.selectbox("نماد", ["همه"] + symbols)
signal_type = st.selectbox("نوع سیگنال", ["همه", "LONG", "SHORT"])
min_profit = st.slider("حداقل سود درصدی", -50.0, 50.0, 0.0, step=0.5)
date_range = st.date_input("بازه تاریخ", [df["entry_time"].min().date(), df["entry_time"].max().date()])

# اعمال فیلترها
filtered = df.copy()
if symbol != "همه":
    filtered = filtered[filtered["symbol"] == symbol]
if signal_type != "همه":
    filtered = filtered[filtered["type"] == signal_type]
filtered = filtered[filtered["profit_pct"] >= min_profit]
filtered = filtered[
    (filtered["entry_time"].dt.date >= date_range[0]) &
    (filtered["entry_time"].dt.date <= date_range[1])
]

st.subheader("📋 جدول سیگنال‌ها")
st.dataframe(filtered, use_container_width=True)

# نمودار قیمت با نقاط ورود/خروج
if symbol != "همه":
    try:
        ohlcv = pd.read_csv(f"data/ohlcv_{symbol}.csv", parse_dates=["Date"])
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=ohlcv["Date"],
            open=ohlcv["Open"],
            high=ohlcv["High"],
            low=ohlcv["Low"],
            close=ohlcv["Close"],
            name="قیمت"
        ))

        for _, row in filtered.iterrows():
            fig.add_trace(go.Scatter(
                x=[row["entry_time"]],
                y=[row["entry_price"]],
                mode="markers",
                marker=dict(color="green" if row["type"]=="LONG" else "red", size=10),
                name=f"{row['type']} Entry"
            ))
            fig.add_trace(go.Scatter(
                x=[row["entry_time"]],
                y=[row["exit_price"]],
                mode="markers",
                marker=dict(color="blue", size=8),
                name="Exit"
            ))

        fig.update_layout(height=600, xaxis_rangeslider_visible=False)
        st.subheader("📊 نمودار قیمت با نقاط سیگنال")
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"نمودار برای نماد {symbol} قابل بارگذاری نیست: {e}")

# گزارش روزانه و تجمیعی
st.subheader("📈 گزارش عملکرد")

if not filtered.empty:
    daily = filtered.groupby(filtered["entry_time"].dt.date).agg({
        "profit_abs": "sum",
        "profit_pct": "mean",
        "symbol": "count"
    }).rename(columns={"symbol": "signal_count"})

    st.write("📅 گزارش روزانه")
    st.dataframe(daily)

    total_profit = filtered["profit_abs"].sum()
    avg_profit_pct = filtered["profit_pct"].mean()
    total_signals = len(filtered)

    st.metric("📊 مجموع سود دلاری", f"${total_profit:.2f}")
    st.metric("📊 میانگین سود درصدی", f"{avg_profit_pct:.2f}%")
    st.metric("📊 تعداد سیگنال‌ها", f"{total_signals}")

    # ذخیره خروجی
    st.download_button("📥 ذخیره خروجی CSV", data=filtered.to_csv(index=False), file_name="filtered_signals.csv", mime="text/csv")
else:
    st.info("هیچ سیگنالی مطابق فیلترها یافت نشد.")

