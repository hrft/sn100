from snl100.binance_loader import fetch_binance_klines
from snl100.signal_engine_v2 import generate_advanced_signal

df = fetch_binance_klines("BTCUSDT", interval="1h", limit=120)
signal = generate_advanced_signal(df)
print("📊 سیگنال پیشرفته:", signal)

