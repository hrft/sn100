import os
from snl100.nobitex_api import fetch_orderbook
import pandas as pd

def fetch_nobitex_orderbook(market):
    return fetch_orderbook(market)

def orderbook_liquidity_metrics(orderbook, top_n=12):
    bids = orderbook.get("bids", [])[:top_n]
    asks = orderbook.get("asks", [])[:top_n]

    def sf(x):
        try:
            return float(x)
        except Exception:
            return 0.0

    bid_sum_quote = sum(sf(p) * sf(q) for p,q in bids)
    ask_sum_quote = sum(sf(p) * sf(q) for p,q in asks)

    best_bid = sf(bids[0][0]) if bids else None
    best_ask = sf(asks[0][0]) if asks else None
    mid = (best_bid + best_ask) / 2.0 if best_bid and best_ask else None

    bid_prices = [sf(p) for p,q in bids] if bids else []
    ask_prices = [sf(p) for p,q in asks] if asks else []
    bid_range = (max(bid_prices) - min(bid_prices)) / (min(bid_prices) if bid_prices and min(bid_prices)!=0 else 1) if len(bid_prices)>1 else 0
    ask_range = (max(ask_prices) - min(ask_prices)) / (min(ask_prices) if ask_prices and min(ask_prices)!=0 else 1) if len(ask_prices)>1 else 0

    return {
        "top_bid_sum_quote": bid_sum_quote,
        "top_ask_sum_quote": ask_sum_quote,
        "top_quote_total": bid_sum_quote + ask_sum_quote,
        "mid_price": mid,
        "bid_depth_price_range": bid_range,
        "ask_depth_price_range": ask_range,
    }

