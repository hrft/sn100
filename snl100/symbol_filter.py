# snl100/symbol_filter.py
from snl100.nobitex_orderbook import fetch_nobitex_orderbook, orderbook_liquidity_metrics
from snl100.nobitex_api import fetch_candles_or_trades
import pandas as pd

def is_symbol_tradeable_nobitex(market,
                                min_top_quote=15000,
                                top_n_depth=12,
                                require_trend=True,
                                allow_orderbook_only=True,
                                trend_ma50_window=50,
                                trend_ma200_window=200,
                                volatility_window=20,
                                min_volatility=0.01):
    result = {"market": market, "ok": False, "reason": None, "metrics": {}}
    try:
        ob = fetch_nobitex_orderbook(market)
    except Exception as e:
        result["reason"] = f"orderbook_error: {e}"
        print(f"⚠️ orderbook error {market}: {e}")
        return result

    metrics = orderbook_liquidity_metrics(ob, top_n=top_n_depth)
    top_quote = metrics.get("top_quote_total", 0.0)
    result["metrics"].update(metrics)

    if top_quote < min_top_quote:
        result["reason"] = f"low_liquidity: top_quote={top_quote:.2f} < {min_top_quote}"
        print(f"❌ نقدشوندگی کم برای {market}: top_quote={top_quote:.2f} < {min_top_quote}")
        return result

    # اگر ترند لازم نیست، قبول کن (orderbook sufficient)
    if not require_trend:
        result.update({"ok": True, "reason": "orderbook_ok", "top_quote": top_quote})
        print(f"✅ انتخاب‌شد بر اساس orderbook: {market} top_quote={top_quote:.2f}")
        return result

    # تلاش برای گرفتن کندل/ترید
    df = fetch_candles_or_trades(market, interval="60", limit=500, days=10)
    if df is None or df.empty:
        if allow_orderbook_only:
            result.update({"ok": True, "reason": "orderbook_only", "top_quote": top_quote})
            print(f"⚠️ کندل برای {market} دردسترس نیست؛ انتخاب بر اساس orderbook (fallback) انجام شد.")
            return result
        result["reason"] = "no_candles_and_trend_required"
        print(f"⚠️ کندل برای {market} دردسترس نیست؛ انتخاب بر اساس orderbook کافی در نظر گرفته نشد.")
        return result

    # محاسبه معیارهای ترند و نوسان
    df = df.sort_index()
    df["MA50"] = df["Close"].rolling(window=trend_ma50_window).mean()
    df["MA200"] = df["Close"].rolling(window=trend_ma200_window).mean()
    df["Volatility"] = (df["High"].rolling(window=volatility_window).max() - df["Low"].rolling(window=volatility_window).min()) / df["Close"].rolling(window=volatility_window).mean()

    last = df.iloc[-1]
    ma50 = last.get("MA50")
    ma200 = last.get("MA200")
    vol = last.get("Volatility") if pd.notna(last.get("Volatility")) else 0.0
    close = last.get("Close")

    result["metrics"].update({"ma50": ma50, "ma200": ma200, "volatility": vol, "close": close})

    if pd.notna(ma200):
        if not (close > ma50 > ma200):
            result["reason"] = f"weak_trend: Close={close}, MA50={ma50}, MA200={ma200}"
            print(f"❌ ترند ضعیف برای {market}: Close={close}, MA50={ma50}, MA200={ma200}")
            return result
    else:
        if not (pd.notna(ma50) and close > ma50):
            result["reason"] = f"weak_trend_no_ma200: Close={close}, MA50={ma50}"
            print(f"❌ ترند ضعیف (بدون MA200) برای {market}: Close={close}, MA50={ma50}")
            return result

    if vol < min_volatility:
        result["reason"] = f"low_volatility: {vol:.4f} < {min_volatility}"
        print(f"❌ نوسان کم برای {market}: Volatility={vol:.4f} < {min_volatility}")
        return result

    result.update({"ok": True, "reason": "trend_ok_with_candles", "top_quote": top_quote})
    print(f"✅ نماد مناسب نوبیتکس: {market} - top_quote={top_quote:.2f}, Volatility={vol:.4f}")
    return result

def filter_symbols_nobitex(markets,
                           min_top_quote=15000,
                           per_symbol_thresholds=None,
                           top_n_depth=12,
                           require_trend=True,
                           allow_orderbook_only=True,
                           **kwargs):
    per_symbol_thresholds = per_symbol_thresholds or {}
    selected = []
    details = []
    for m in markets:
        thresh = per_symbol_thresholds.get(m, min_top_quote)
        res = is_symbol_tradeable_nobitex(m,
                                          min_top_quote=thresh,
                                          top_n_depth=top_n_depth,
                                          require_trend=require_trend,
                                          allow_orderbook_only=allow_orderbook_only,
                                          **kwargs)
        details.append(res)
        if res.get("ok"):
            selected.append({"market": m, "reason": res.get("reason"), "threshold": thresh, "metrics": res.get("metrics")})
        else:
            print(f"⛔ رد شد {m} با آستانه {thresh} دلیل: {res.get('reason')}")
    print(f"📊 نمادهای انتخاب‌شده: {[s['market'] for s in selected]}")
    return [s["market"] for s in selected], details

