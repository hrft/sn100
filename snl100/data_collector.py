import requests
from requests.adapters import HTTPAdapter, Retry

NOBITEX_URL = "https://apiv2.nobitex.ir/v3/orderbook"
TABDEAL_URL = "https://api1.tabdeal.org/r/api/v1/depth"

session = requests.Session()
session.mount("https://", HTTPAdapter(max_retries=Retry(
    total=2, backoff_factor=0.3, status_forcelist=[429, 500, 502, 503, 504]
)))

def _get_json(url, timeout=4):
    try:
        r = session.get(url, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"⚠️ GET error: {url} → {e}")
        return None

def check_nobitex(symbol="BTCUSDT"):
    data = _get_json(f"{NOBITEX_URL}/{symbol}")
    return data and "lastTradePrice" in data and data["lastTradePrice"] not in (None, "", 0)

def check_tabdeal(symbol="BTCUSDT", limit=1):
    data = _get_json(f"{TABDEAL_URL}?symbol={symbol}&limit={limit}")
    if not data:
        return False
    if "last" in data and data["last"]:
        return True
    bids = data.get("bids", [])
    asks = data.get("asks", [])
    return bool(bids) and bool(asks) and float(bids[0][0]) > 0 and float(asks[0][0]) > 0

def check_all_sources(symbol="BTCUSDT"):
    return {
        "nobitex": check_nobitex(symbol),
        "tabdeal": check_tabdeal(symbol),
    }

def fetch_nobitex_price(symbol):
    data = _get_json(f"{NOBITEX_URL}/{symbol}")
    if data and data.get("lastTradePrice"):
        try:
            return float(data["lastTradePrice"])
        except Exception:
            pass
    return None

def fetch_tabdeal_price(symbol, limit=50):
    data = _get_json(f"{TABDEAL_URL}?symbol={symbol}&limit={limit}")
    if not data:
        return None
    if "last" in data and data["last"]:
        try:
            return float(data["last"])
        except Exception:
            pass
    bids = data.get("bids", [])
    asks = data.get("asks", [])
    if bids and asks:
        try:
            best_bid = float(bids[0][0])
            best_ask = float(asks[0][0])
            return (best_bid + best_ask) / 2.0
        except Exception:
            pass
    return None

def fetch_price(symbol):
    price = fetch_nobitex_price(symbol)
    if price is not None:
        return round(price, 6)
    price = fetch_tabdeal_price(symbol)
    if price is not None:
        return round(price, 6)
    print(f"⚠️ SourceDown: قیمت برای {symbol} در دسترس نیست.")
    return None

