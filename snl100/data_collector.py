import requests
from requests.adapters import HTTPAdapter, Retry

# منبع داده: بایننس (دلاری، عمومی، پایدار)
BINANCE_BOOKTICKER = "https://api.binance.com/api/v3/ticker/bookTicker"

session = requests.Session()
session.mount("https://", HTTPAdapter(max_retries=Retry(
    total=2, backoff_factor=0.3, status_forcelist=[429, 500, 502, 503, 504]
)))

def _get_json(url, params=None, timeout=4):
    try:
        r = session.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"⚠️ GET error: {url} → {e}")
        return None

def check_source(symbol="BTCUSDT"):
    data = _get_json(BINANCE_BOOKTICKER, params={"symbol": symbol})
    if not data:
        return False
    try:
        bid = float(data["bidPrice"])
        ask = float(data["askPrice"])
        return bid > 0 and ask > 0
    except Exception:
        return False

def fetch_price(symbol):
    data = _get_json(BINANCE_BOOKTICKER, params={"symbol": symbol})
    if not data:
        return None
    try:
        bid = float(data["bidPrice"])
        ask = float(data["askPrice"])
        mid = (bid + ask) / 2.0
        return round(mid, 6)
    except Exception:
        return None

