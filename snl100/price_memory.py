import os
import json
from collections import deque

MEMORY_FILE = "data/price_memory.json"
MAX_LENGTH = 100

def ensure_dirs():
    os.makedirs("data", exist_ok=True)

def load_memory():
    ensure_dirs()
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
    memory = {}
    for symbol, prices in raw.items():
        memory[symbol] = deque(prices, maxlen=MAX_LENGTH)
    return memory

def save_memory(memory):
    raw = {symbol: list(prices) for symbol, prices in memory.items()}
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(raw, f, indent=2)

def append_price(memory, symbol, price):
    if symbol not in memory:
        memory[symbol] = deque(maxlen=MAX_LENGTH)
    memory[symbol].append(price)
    save_memory(memory)

def get_prices(memory, symbol):
    return list(memory.get(symbol, []))

