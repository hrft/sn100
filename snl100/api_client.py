# snl100/api_client.py
import os
import time
import requests
import pandas as pd
from datetime import datetime
from .config import REQUEST_DELAY

API_BASE = os.getenv("NOBITEX_API_BASE", "https://apiv2.nobitex.ir")
DEFAULT_TIMEOUT = 15

# چند مسیر متداول که ممکن است API نوبیتکس از آن‌ها استفاده کند
CANDLES_ENDPOINTS = [
    "/market/history",             # احتمالی (market/history?market=BTCUSDT...)
    "/market/candles",             # احتمالی دیگر (candles?market=...)
    "/market/udf/history",         # endpoint که در کد فعلی استفاده شده
    "/public/market/history",      # جایگزین فرضی
    "/market/kline",               # جایگزین فرضی
]

# چند قالب هدر متداول
def build_headers(token):
    if not token:
        return [{}]
    return [
        {"Authorization": f"Bearer {token}"},
        {"Authorization": f"Token {token}"},
        {"X-API-KEY": token},
        {"x-api-key": token},
    ]

def _to_dataframe_from_generic_candles(data):
    """
    تبدیل چند فرمت متداول JSON کندل به DataFrame استاندارد
    انتظار: list of [timestamp, open, high, low, close, volume] یا list of dicts
    """
    if data is None:
        return None

    # اگر data خودش dict و کلیدی مثل 'data' یا 'candles' دارد، سعی کن آن را استخراج کنی
    if isinstance(data, dict):
        for k in ("data", "candles", "result", "items"):
            if k in data and isinstance(data[k], (list, dict)):
                data = data[k]
                break

    # اگر داده لیستی از لیست‌هاست (kline style)
    if isinstance(data, list) and data and isinstance(data[0], (list, tuple)):
        # انتظار: [ts, open, high, low, close, volume] یا بعضی اکسچنج‌ها [openTime,...]
        rows = []
        for row in data:
            try:
                ts = int(row[0])
                # تبدیل مقادیر به float با محافظت
                open_, high, low, close, vol = map(float, row[1:6])
            except Exception:
                continue
            rows.append({"Date": pd.to_datetime(ts, unit="s"), "Open": open_, "High": high, "Low": low, "Close": close, "Volume": vol})
        return pd.DataFrame(rows).set_index("Date")

    # اگر لیست از دیکت‌هاست و کلیدهای مشخص دارد
    if isinstance(data, list) and data and isinstance(data[0], dict):
        df = pd.DataFrame(data)
        # احتمالات نام‌گذاری timestamp
        if "timestamp" in df.columns:
            df["Date"] = pd.to_datetime(df["timestamp"], unit="ms", errors="coerce")
        elif "time" in df.columns:
            df["Date"] = pd.to_datetime(df["time"], unit="s", errors="coerce")
        elif "t" in df.columns:
            df["Date"] = pd.to_datetime(df["t"], unit="s", errors="coerce")
        # نام‌های احتمالی قیمت
        for col in df.columns:
            low = col.lower()
            if low in ("open","o"):
                df = df.rename(columns={col: "Open"})
            if low in ("high","h"):
                df = df.rename(columns={col: "High"})
            if low in ("low","l"):
                df = df.rename(columns={col: "Low"})
            if low in ("close","c"):
                df = df.rename(columns={col: "Close"})
            if low in ("volume","v"):
                df = df.rename(columns={col: "Volume"})
            if low in ("quotevolume","q", "quoteVolume"):
                df = df.rename(columns={col: "QuoteVolume"})
        expected = ["Date","Open","High","Low","Close","Volume"]
        for c in expected:
            if c not in df.columns:
                df[c] = None
        df = df[expected]
        df = df.dropna(subset=["Date"]).set_index("Date")
        # تبدیل مقادیر به float با محافظت
        for c in ["Open","High","Low","Close","Volume"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        return df

    # در غیر این صورت برگرد None
    return None

class NobitexAPI:
    def __init__(self, token=None, api_base=None, delay=None, timeout=DEFAULT_TIMEOUT):
        self.token = token or os.getenv("NOBITEX_TOKEN")
        self.api_base = api_base or API_BASE
        self.delay = delay or REQUEST_DELAY
        self.timeout = timeout

    def _try_request(self, path, params=None, headers=None):
        url = self.api_base.rstrip("/") + path
        try:
            r = requests.get(url, params=params, headers=headers, timeout=self.timeout)
        except Exception as e:
            return {"ok": False, "error": f"request-exception: {e}", "status": None, "text": None}
        time.sleep(self.delay)
        return {"ok": True, "status": r.status_code, "text": r.text, "json": None if r.text == "" else self._safe_json(r), "resp": r}

    def _safe_json(self, resp):
        try:
            return resp.json()
        except Exception:
            try:
                return requests.json.loads(resp.text)
            except Exception:
                return None

    def fetch_ohlc(self, symbol="BTCUSDT", resolution="60", days=7):
        # تبدیل resolution به پارامترهای مورد نیاز هر endpoint اگر لازم باشه
        to_ts = int(time.time())
        from_ts = to_ts - int(days) * 24 * 3600
        params_variants = [
            {"market": symbol, "interval": resolution, "limit": 500},
            {"symbol": symbol, "resolution": resolution, "from": from_ts, "to": to_ts},
            {"market": symbol, "from": from_ts, "to": to_ts, "limit": 500},
            {"symbol": symbol, "from": from_ts, "to": to_ts, "resolution": resolution},
        ]

        headers_list = build_headers(self.token)

        # تلاش در ترکیب‌های مختلف endpoint + header + پارامتر
        for hdr in headers_list:
            for ep in CANDLES_ENDPOINTS:
                for params in params_variants:
                    res = self._try_request(ep, params=params, headers=hdr)
                    if not res["ok"]:
                        continue
                    status = res["status"]
                    if status == 200 and res["json"] is not None:
                        df = _to_dataframe_from_generic_candles(res["json"])
                        if df is not None and not df.empty:
                            return df
                        # اگر json dict با کلید data بود سعی کن آن را تبدیل کنی
                        if isinstance(res["json"], dict):
                            # جستجوی عمیق برای لیست کندل
                            for key in ("data","candles","result","items"):
                                if key in res["json"]:
                                    df = _to_dataframe_from_generic_candles(res["json"][key])
                                    if df is not None and not df.empty:
                                        return df
                        # اگر رسیدیم اینجا، داده نامشخص بود؛ لاگ بزن و ادامه بده
                        print(f"DEBUG: 200 but couldn't parse JSON for {ep} with headers {hdr} and params {params}")
                        continue
                    # اگر 404 یا 401 یا 403 یا 429، لاگ کن ولی تلا‌ش بعدی را ادامه بده
                    if status in (401,403,404,429,500):
                        print(f"DEBUG: {status} from {self.api_base + ep} with headers={hdr} params={params} resp_snippet={res['text'][:200]}")
                        continue
        # اگر همه ترکیبات شکست خوردند، برگرد None و لاگ کامل بده
        print("ERROR: Unable to fetch usable OHLC from Nobitex with tried endpoints/headers.")
        return None

