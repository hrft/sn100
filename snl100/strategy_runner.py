import pandas as pd
from snl100.indicator_engine import enrich_dataframe
from snl100.signal_executor import decide_signal_from_indicators

def run_strategies(prices):
    if not prices or len(prices) < 5:
        last = prices[-1] if prices else None
        return {"signal": "hold", "target": last, "stop": last, "strategy": "InsufficientData", "confidence": 0.3}
    df = pd.DataFrame({"price": prices})
    enriched = enrich_dataframe(df)
    row = enriched.iloc[-1].to_dict()
    return decide_signal_from_indicators(row)

