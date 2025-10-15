import pandas as pd

def ema(series, span):
    return series.ewm(span=span, adjust=False).mean()

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

def calculate_volatility(prices, window=10):
    return prices.pct_change().rolling(window=window).std()

def calculate_macd(prices, fast=12, slow=26, signal=9):
    macd_line = ema(prices, fast) - ema(prices, slow)
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def enrich_dataframe(df):
    df = df.copy()
    prices = df["price"]
    df["rsi"] = calculate_rsi(prices)
    df["ma_fast"] = calculate_ma(prices, window=5)
    df["ma_slow"] = calculate_ma(prices, window=20)
    df["volatility"] = calculate_volatility(prices)
    macd_line, signal_line, hist = calculate_macd(prices)
    df["macd"] = macd_line
    df["macd_signal"] = signal_line
    df["macd_hist"] = hist
    return df

