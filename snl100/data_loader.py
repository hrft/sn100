import pandas as pd
import os

def load_from_csv(filepath):
    """
    بارگذاری داده از فایل CSV
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ فایل پیدا نشد: {filepath}")
    df = pd.read_csv(filepath, parse_dates=["Date"])
    return df


def generate_sample_data(trend="up", periods=60):
    """
    تولید داده تستی برای روند صعودی، نزولی یا خنثی
    """
    base = 100
    if trend == "up":
        close = [base + i for i in range(periods)]
        volume = [100]*periods
        volume[-1] = 500  # حجم بالا در کندل آخر
    elif trend == "down":
        close = [base - i for i in range(periods)]
        volume = [100]*periods
        volume[-1] = 500
    else:
        close = [base]*periods
        volume = [100]*periods

    df = pd.DataFrame({
        "Date": pd.date_range("2025-10-01", periods=periods, freq="15min"),
        "Open": close,
        "High": [c + 1 for c in close],
        "Low": [c - 1 for c in close],
        "Close": close,
        "Volume": volume
    })
    return df

