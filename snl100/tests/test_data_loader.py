import pandas as pd
from snl100.data_loader import generate_sample_data, load_from_csv
import os

def test_generate_sample_data_up():
    df = generate_sample_data("up", periods=60)
    print("📊 خروجی سیگنال:", result)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 60
    assert df["Close"].iloc[-1] > df["Close"].iloc[0]
    assert df["Volume"].iloc[-1] > df["Volume"].mean()

def test_generate_sample_data_down():
    df = generate_sample_data("down", periods=60)
    print("📊 خروجی سیگنال:", result)
    assert df["Close"].iloc[-1] < df["Close"].iloc[0]
    assert df["Volume"].iloc[-1] > df["Volume"].mean()

def test_load_from_csv(tmp_path):
    # ساخت فایل تستی CSV
    test_file = tmp_path / "sample.csv"
    df = generate_sample_data("flat", periods=10)
    df.to_csv(test_file, index=False)

    # تست بارگذاری
    loaded = load_from_csv(test_file)
    print("📊 خروجی سیگنال:", result)
    assert isinstance(loaded, pd.DataFrame)
    assert len(loaded) == 10
    assert "Date" in loaded.columns

