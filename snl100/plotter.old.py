# Plot candlestick chart
import plotly.graph_objects as go
import pandas as pd
import os

def plot_signal(df, signal_data, symbol="BTCUSDT", output_path="output/signal_chart.html"):
    df = df.copy()
    df["MA50"] = df["Close"].rolling(window=50).mean()

    fig = go.Figure()

    # کندل‌استیک
    fig.add_trace(go.Candlestick(
        x=df["Date"],
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Candles"
    ))

    # MA50
    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["MA50"],
        mode="lines",
        name="MA50",
        line=dict(color="blue", width=1)
    ))

    # نقاط سیگنال
    if signal_data["signal"] in ["buy", "sell"]:
        color = "green" if signal_data["signal"] == "buy" else "red"
        fig.add_trace(go.Scatter(
            x=[df["Date"].iloc[-1]],
            y=[signal_data["entry"]],
            mode="markers+text",
            name="Entry",
            marker=dict(color=color, size=10),
            text=[f"{signal_data['signal'].upper()}"],
            textposition="top center"
        ))

    fig.update_layout(
        title=f"Signal Chart for {symbol}",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_dark",
        height=600
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.write_html(output_path)
    print(f"✅ نمودار ذخیره شد: {output_path}")

