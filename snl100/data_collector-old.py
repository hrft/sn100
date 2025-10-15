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

def fetch_usdt_irt():
    # اول v3، اگر نشد v2
    for base in (NOBITEX_V3, NOBITEX_V2):
        data = _get_json(f"{base}/USDTIRT")
        if data and data.get("lastTradePrice"):
            return float(data["lastTradePrice"])
    print("❌ USDTIRT در دسترس نیست.")
    return None

def fetch_nobitex_price(symbol):
    for base in (NOBITEX_V3, NOBITEX_V2):
        data = _get_json(f"{base}/{symbol}")
        if data and data.get("lastTradePrice"):
            return float(data["lastTradePrice"])
    return None

def fetch_tabdeal_price(symbol):
    data = _get_json(TABDEAL_URL)
    if not data or "result" not in data:
        return None
    for item in data["result"]:
        if item.get("symbol", "").upper() == symbol.upper():
            return float(item["last"])
    return None

def fetch_price_usdt(symbol):
    usdt_irt = fetch_usdt_irt()
    if not usdt_irt:
        return None
    price_irt = fetch_nobitex_price(symbol) or fetch_tabdeal_price(symbol)
    if price_irt is None:
        print(f"⚠️ Price not available for {symbol}")
        return None
    return round(price_irt / usdt_irt, 6)

