import pandas as pd
from snl100.signal_engine import generate_signal

def make_test_df(trend="up"):
    """
    تولید داده‌ی تستی برای روند صعودی، نزولی یا خنثی
    """
    base = 100
    if trend == "up":
        close = [base + i for i in range(60)]
        volume = [100]*50 + [500]*10
    elif trend == "down":
        close = [base - i for i in range(60)]
        volume = [100]*50 + [500]*10
    else:
        close = [base]*60
        volume = [100]*60

    df = pd.DataFrame({
        "Date": pd.date_range("2025-10-01", periods=60, freq="15min"),
        "Open": close,
        "High": [c + 1 for c in close],
        "Low": [c - 1 for c in close],
        "Close": close,
        "Volume": volume
    })
    return df

def test_buy_signal():
    df = make_test_df("up")
    result = generate_signal(df)
    print("📈 تست خرید:", result)
    assert result["signal"] == "buy"
    assert result["entry"] is not None
    assert result["stop"] < result["entry"]
    assert result["target"] > result["entry"]

def test_sell_signal():
    df = make_test_df("down")
    result = generate_signal(df)
    print("📉 تست فروش:", result)
    assert result["signal"] == "sell"
    assert result["entry"] is not None
    assert result["stop"] > result["entry"]
    assert result["target"] < result["entry"]

def test_no_signal():
    df = make_test_df("flat")
    result = generate_signal(df)
    print("⛔ تست بدون سیگنال:", result)
    assert result["signal"] is None
    assert result["entry"] is None
    assert result["stop"] is None
    assert result["target"] is None

