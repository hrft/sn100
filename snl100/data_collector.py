import requests
import time

NOBITEX_URL = "https://apiv2.nobitex.ir/v3/orderbook"
TABDEAL_URL = "https://api1.tabdeal.org/api/v1/rest/tickers"

SYMBOLS_IRT = ["BTCIRT", "ETHIRT", "BNBIRT", "XRPIRT", "DOGEIRT"]

def fetch_nobitex(symbol):
    try:
        url = f"{NOBITEX_URL}/{symbol}"
        response = requests.get(url, timeout=5)
        data = response.json()
        return {
            "symbol": symbol,
            "price": float(data["lastTradePrice"]),
            "volume": float(data.get("baseVolume", 0)),
            "source": "nobitex"
        }
    except Exception as e:
        print(f"❌ Nobitex error for {symbol}: {e}")
        return None

def fetch_tabdeal(symbol):
    try:
        response = requests.get(TABDEAL_URL, timeout=5)
        data = response.json()
        for item in data["result"]:
            if item["symbol"].upper() == symbol:
                return {
                    "symbol": symbol,
                    "price": float(item["last"]),
                    "volume": float(item.get("volume", 0)),
                    "source": "tabdeal"
                }
        return None
    except Exception as e:
        print(f"❌ Tabdeal error for {symbol}: {e}")
        return None

def fetch_usdt_irt():
    try:
        url = f"{NOBITEX_URL}/USDTIRT"
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data["lastTradePrice"])
    except Exception as e:
        print(f"❌ USDTIRT fetch error: {e}")
        return None

def collect_data():
    usdt_irt = fetch_usdt_irt()
    if not usdt_irt:
        print("⚠️ نرخ USDTIRT در دسترس نیست.")
        return []

    results = []
    for symbol in SYMBOLS_IRT:
        data = fetch_nobitex(symbol)
        if data is None:
            data = fetch_tabdeal(symbol)
        if data:
            data["price_usdt"] = round(data["price"] / usdt_irt, 4)
            results.append(data)
    return results

if __name__ == "__main__":
    print("📡 جمع‌آوری داده‌های زنده...")
    data = collect_data()
    for item in data:
        print(f"{item['symbol']} → {item['price_usdt']} USDT | Volume: {item['volume']} | Source: {item['source']}")

