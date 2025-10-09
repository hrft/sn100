import os
import time
import requests
import pandas as pd

API_BASE = os.getenv("NOBITEX_API_BASE", "https://apiv2.nobitex.ir")
NOBITEX_TOKEN = os.getenv("NOBITEX_TOKEN", None)
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", 0.12))
TIMEOUT = 12

# مسیرهای احتمالی کندل و ترید که امتحان می‌شوند
CANDLES_ENDPOINTS = [
    "/v3/candles",            # احتمالی: ?market=BTCUSDT&interval=60&limit=200
    "/v3/trades",             # احتمالی: ?market=BTCUSDT&limit=500
    "/v3/history",            # احتمالی
    "/v3/market/trades",      # احتمالی
    "/v3/market/candles",     # احتمالی
]

def _headers(token):
    if not token:
        return {}
    # امتحان فرمت متداول Token و Bearer و X-API-KEY
    # برای درخواست‌های جداگانه header را به طور صریح می‌دهیم
    return {"Authorization": f"Bearer {token}"}

def _try_get(path, params=None, headers=None):
    url = API_BASE.rstrip("/") + path
    try:
        r = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
    except Exception as e:
        return {"ok": False, "status": None, "text": str(e), "json": None}
    time.sleep(REQUEST_DELAY)
    json_body = None
    try:
        json_body = r.json()
    except Exception:
        json_body = None
    return {"ok": True, "status": r.status_code, "text": r.text, "json": json_body, "resp": r}

def _to_df_from_generic(data):
    if data is None:
        return None

    # اگر dict شامل کلیدهای متداول است، تلاش برای استخراج لیست کندل
    if isinstance(data, dict):
        for k in ("data", "candles", "result", "items", "trades"):
            if k in data and isinstance(data[k], (list, tuple)):
                data = data[k]
                break

    # لیست از لیست ها
    if isinstance(data, list) and data and isinstance(data[0], (list, tuple)):
        rows = []
        for row in data:
            # انتظار رایج: [ts, open, high, low, close, volume] یا [openTime, open, high, low, close, volume]
            try:
                ts = int(row[0])
                open_, high, low, close, vol = map(float, row[1:6])
            except Exception:
                continue
            rows.append({"Date": pd.to_datetime(ts, unit="s"), "Open": open_, "High": high, "Low": low, "Close": close, "Volume": vol})
        if not rows:
            return None
        df = pd.DataFrame(rows).set_index("Date")
        return df

    # لیست از دیکشنری‌ها
    if isinstance(data, list) and data and isinstance(data[0], dict):
        df = pd.DataFrame(data)
        # timestamp نام‌های متداول
        if "timestamp" in df.columns:
            df["Date"] = pd.to_datetime(df["timestamp"], unit="ms", errors="coerce")
        elif "time" in df.columns:
            df["Date"] = pd.to_datetime(df["time"], unit="s", errors="coerce")
        elif "t" in df.columns:
            df["Date"] = pd.to_datetime(df["t"], unit="s", errors="coerce")
        # نقشه‌گذاری ستون قیمت
        colmap = {}
        for c in df.columns:
            lc = c.lower()
            if lc in ("open", "o"):
                colmap[c] = "Open"
            if lc in ("high", "h"):
                colmap[c] = "High"
            if lc in ("low", "l"):
                colmap[c] = "Low"
            if lc in ("close", "c"):
                colmap[c] = "Close"
            if lc in ("volume", "v"):
                colmap[c] = "Volume"
            if lc in ("quotevolume", "q", "quote_volume"):
                colmap[c] = "QuoteVolume"
        df = df.rename(columns=colmap)
        expected = ["Date", "Open", "High", "Low", "Close", "Volume"]
        for e in expected:
            if e not in df.columns:
                df[e] = None
        df = df[expected]
        df = df.dropna(subset=["Date"]).set_index("Date")
        for c in ["Open","High","Low","Close","Volume"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        return df

    return None

def fetch_orderbook(market):
    path = f"/v3/orderbook/{market}"
    res = _try_get(path, headers=_headers(NOBITEX_TOKEN))
    if not res["ok"]:
        raise RuntimeError(f"request failed: {res['text']}")
    if res["status"] != 200:
        raise RuntimeError(f"orderbook status {res['status']} {res['text'][:200]}")
    return res["json"]

def fetch_candles_or_trades(market, interval="60", limit=500, days=7):
    # تلاش برای چند endpoint و ترکیب پارامترها تا زمانی که داده قابل‌تبدیل بدست آید
    to_ts = int(time.time())
    from_ts = to_ts - int(days) * 24 * 3600
    params_variants = [
        {"market": market, "interval": interval, "limit": limit},
        {"market": market, "from": from_ts, "to": to_ts, "limit": limit},
        {"symbol": market, "resolution": interval, "from": from_ts, "to": to_ts},
        {"symbol": market, "limit": limit},
    ]
    for params in params_variants:
        for ep in CANDLES_ENDPOINTS:
            res = _try_get(ep, params=params, headers=_headers(NOBITEX_TOKEN))
            if not res["ok"]:
                continue
            status = res["status"]
            if status == 200 and res["json"] is not None:
                df = _to_df_from_generic(res["json"])
                if df is not None and not df.empty:
                    return df
                # اگر payload dict است، نگاه دقیق‌تر کن
                if isinstance(res["json"], dict):
                    for k in ("data","candles","items","result","trades"):
                        if k in res["json"]:
                            df = _to_df_from_generic(res["json"][k])
                            if df is not None and not df.empty:
                                return df
                # اگر نتوانستیم تبدیل کنیم ادامه بده
                continue
            # لاگ مفید برای دیباگ
            if status is not None:
                print(f"DEBUG nobitex {ep} returned {status} for params {params} snippet {res['text'][:160]}")
    # اگر همه شکست خوردند برگرد None
    return None

