import os
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

def plot_signal(df, signal, symbol, output_path=None):
    os.makedirs("output/signals", exist_ok=True)

    if output_path is None:
        output_path = f"output/signals/{symbol}_chart.html"

    fig = go.Figure()

    if df is not None and not df.empty:
        fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Close"))
        fig.update_layout(title=f"Signal Chart: {symbol}", xaxis_title="Time", yaxis_title="Price")
    else:
        # ساخت placeholder ساده برای حالت بدون داده
        fig.add_annotation(text="No candle data available",
                           xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False,
                           font=dict(size=20))
        fig.update_layout(title=f"Signal Chart: {symbol} (Fallback)",
                          xaxis=dict(visible=False),
                          yaxis=dict(visible=False))

    fig.write_html(output_path)
    print(f"📈 چارت ذخیره شد: {output_path}")

