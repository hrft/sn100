import pandas as pd
from snl100.signal_engine import generate_signal

def test_buy_signal():
    import pandas as pd
    from snl100.signal_engine import generate_signal

    # ساخت داده صعودی با شکست سقف و حجم بالا
    data = {
        "Date": pd.date_range("2025-10-01", periods=60, freq="15min"),
        "Open": [100 + i for i in range(60)],
        "High": [101 + i for i in range(60)],
        "Low": [99 + i for i in range(60)],
        "Close": [100 + i for i in range(60)],
        "Volume": [100]*40 + [300]*20  # حجم بالا در انتها
    }
    df = pd.DataFrame(data)
    result = generate_signal(df)
    assert result["signal"] == "buy"
    assert result["entry"] is not None
    assert result["stop"] < result["entry"]
    assert result["target"] > result["entry"]

def test_sell_signal():
    import pandas as pd
    from snl100.signal_engine import generate_signal

    # ساخت داده نزولی با شکست کف و حجم بالا
    data = {
        "Date": pd.date_range("2025-10-01", periods=60, freq="15min"),
        "Open": [200 - i for i in range(60)],
        "High": [201 - i for i in range(60)],
        "Low": [199 - i for i in range(60)],
        "Close": [200 - i for i in range(60)],
        "Volume": [100]*40 + [300]*20
    }
    df = pd.DataFrame(data)
    result = generate_signal(df)
    assert result["signal"] == "sell"
    assert result["entry"] is not None
    assert result["stop"] > result["entry"]
    assert result["target"] < result["entry"]

def test_no_signal():
    # داده‌ای که نه شکست داره نه حجم بالا
    data = {
        "Date": pd.date_range("2025-10-01", periods=60, freq="15min"),
        "Open": [100]*60,
        "High": [101]*60,
        "Low": [99]*60,
        "Close": [100]*60,
        "Volume": [100]*60
    }
    df = pd.DataFrame(data)
    result = generate_signal(df)
    assert result["signal"] is None

