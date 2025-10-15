def position_size(balance, entry, stop, risk_pct=0.01):
    risk_per_trade = balance * risk_pct
    stop_distance = abs(entry - stop)
    if stop_distance <= 0:
        return 0
    size = risk_per_trade / stop_distance
    return round(size, 6)

def risk_reward(entry, target, stop):
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = reward / risk if risk > 0 else 0
    return round(rr, 3), round(risk, 6), round(reward, 6)

