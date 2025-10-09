from snl100.symbol_filter import filter_symbols_nobitex
markets = ["BTCUSDT","ETHUSDT","XRPUSDT","SOLUSDT","BNBUSDT","DOGEUSDT"]
print(filter_symbols_nobitex(markets, min_top_quote=20000, top_n_depth=12, require_trend=True))

