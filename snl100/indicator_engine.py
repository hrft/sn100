import pandas as pd
import numpy as np

def calculate_rsi(prices, window=14):
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_ma(prices, window=5):
    return prices.rolling(window=window).mean()

def calculate_atr(highs, lows, closes, window=14):
    tr1 = highs - lows
    tr2 = abs(highs - closes.shift())
    tr3 = abs(lows - closes.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=window).mean()
    return atr

def calculate_volatility(prices, window=10):
    return prices.pct_change().rolling(window=window).std()

def enrich_dataframe(df):
    df = df.copy()
    df["rsi"] = calculate_rsi(df["price"])
    df["ma_fast"] = calculate_ma(df["price"], window=5)
    df["ma_slow"] = calculate_ma(df["price"], window=20)
    df["volatility"] = calculate_volatility(df["price"])
    return df

