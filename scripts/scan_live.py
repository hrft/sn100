#!/usr/bin/env python3

import argparse, os
import pandas as pd
from snl100.signal_engine import generate_signal
from fasrom.api_client import NobitexClient
from fasrom.ohlc import json_to_ohlc
from fasrom.plotter import make_candlestick_html

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--symbol", default="BTCUSDT")
    p.add_argument("--resolution", default="15")
    p.add_argument("--days", type=int, default=3)
    p.add_argument("--out_html", default="output/html/snl100.html")
    p.add_argument("--out_csv", default="signals/snl100.csv")
    args = p.parse_args()

    client = NobitexClient()
    j = client.get_ohlc(symbol=args.symbol, resolution=args.resolution, days=args.days)

    df = json_to_ohlc(j)

    if df is None or df.empty:
        print("❌ داده‌ای دریافت نشد.")
        return

    result = generate_signal(df)
    print("📊 سیگنال:", result)

    # ذخیره HTML
    os.makedirs(os.path.dirname(args.out_html), exist_ok=True)
    make_candlestick_html(
        df, args.out_html,
        symbol=args.symbol,
        entry=result["entry"],
        stop=result["stop"],
        target=result["target"],
        signal_type="خرید" if result["signal"] == "buy" else "فروش"
    )

    # ذخیره CSV
    os.makedirs(os.path.dirname(args.out_csv), exist_ok=True)
    pd.DataFrame([result]).to_csv(args.out_csv, index=False)
    print(f"✅ خروجی ذخیره شد: {args.out_html} و {args.out_csv}")

if __name__ == "__main__":
    main()

