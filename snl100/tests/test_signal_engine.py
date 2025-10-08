# Unit tests for signal engine
import pandas as pd
from snl100.signal_engine import generate_signal
from snl100.data_loader import generate_sample_data

def test_buy_signal():
    df = generate_sample_data("up", periods=60)
    result = generate_signal(df)
    assert isinstance(result, dict)
    assert result["signal"] == "buy"
    assert result["entry"] is not None
    assert result["stop"] < result["entry"]
    assert result["target"] > result["entry"]

def test_sell_signal():
    df = generate_sample_data("down", periods=60)
    result = generate_signal(df)
    assert result["signal"] == "sell"
    assert result["entry"] is not None
    assert result["stop"] > result["entry"]
    assert result["target"] < result["entry"]

def test_no_signal():
    df = generate_sample_data("flat", periods=60)
    result = generate_signal(df)
    assert result["signal"] is None
    assert result["entry"] is None
    assert result["stop"] is None
    assert result["target"] is None

