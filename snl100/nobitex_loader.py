import os
import requests
import pandas as pd
from datetime import datetime

NOBITEX_TOKEN = os.getenv("NOBITEX_TOKEN")
NOBITEX_API_BASE = os.getenv("NOBITEX_API_BASE", "https://apiv2.nobitex.ir")

def fetch_nobitex_klines(symbol, interval="1h", limit=300):
    """
    adapter ساده برای گرفتن کندل از نوبیتکس
    خروجی: DataFrame با ستون های Date, Open, High, Low, Close, Volume
    توجه: endpoint و پارامترها را طبق مستندات نوبیتکس اگر فرق داشت تنظیم کن
    """
    # نمونه endpoint فرضی؛ اگر API تو ساختار دیگری دارد آن را جایگزین کن
    url = f"{NOBITEX_API_BASE}/market/history/{symbol}"
    headers = {"Authorization": f"Bearer {NOBITEX_TOKEN}"} if NOBITEX_TOKEN else {}
    params = {"interval": interval, "limit": limit}

    r = requests.get(url, headers=headers, params=params, timeout=15)
    r.raise_for_status()
    payload = r.json()

    # فرض ساختار: payload["data"] -> list of candles with timestamp, open, high, low, close, volume
    data = payload.get("data", payload)
    if not isinstance(data, list):
        raise ValueError("Unexpected response structure from Nobitex API")

    df = pd.DataFrame(data)
    # اگر نام فیلدها فرق داشت، این‌جا نگاشت را تغییر بده
    # فرض: timestamp in ms, open, high, low, close, volume
    if "timestamp" in df.columns:
        df["Date"] = pd.to_datetime(df["timestamp"], unit="ms")
    elif "time" in df.columns:
        df["Date"] = pd.to_datetime(df["time"], unit="s")
    else:
        df["Date"] = pd.to_datetime(df.get("date", pd.Series([None]*len(df))))

    # استانداردسازی ستون‌ها به حروف بزرگ شروع
    mapping = {}
    for col in df.columns:
        lower = col.lower()
        if lower in ("open","high","low","close","volume"):
            mapping[col] = lower.capitalize()

    df = df.rename(columns=mapping)
    expected = ["Date","Open","High","Low","Close","Volume"]
    for c in expected:
        if c not in df.columns:
            df[c] = 0.0

    df = df[expected]
    df = df.astype({"Open":float,"High":float,"Low":float,"Close":float,"Volume":float})
    return df

