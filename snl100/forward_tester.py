import os, csv, time
from datetime import datetime

from snl100.config import USDT_SYMBOLS, OUTPUT_LOG, REFRESH_SECONDS
from snl100.signal_pipeline import get_signal
from snl100.risk_manager import position_size, risk_reward

def ensure_dirs():
    os.makedirs("output", exist_ok=True)

def log_signal(row):
    write_header = not os.path.exists(OUTPUT_LOG)
    with open(OUTPUT_LOG, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(row)

def run_forward_test(balance=1000.0, steps=200):
    ensure_dirs()
    print("🚀 تست زنده روی جفت‌ارزهای دلاری (USDT pairs)...")
    for _ in range(steps):
        for symbol in USDT_SYMBOLS:
            s = get_signal(symbol)
            if s["price"] is None or s["target"] is None or s["stop"] is None:
                rr, risk_abs, reward_abs = 0, 0, 0
                size, expected_loss, profit = 0, 0, 0
            else:
                rr, risk_abs, reward_abs = risk_reward(s["price"], s["target"], s["stop"])
                size = position_size(balance, s["price"], s["stop"], risk_pct=0.01)
                expected_loss = round(size * risk_abs, 6)
                # سود تخمینی ساده تا تارگت
                if s["signal"] == "buy":
                    profit = (s["target"] - s["price"]) * size
                elif s["signal"] == "sell":
                    profit = (s["price"] - s["target"]) * size
                else:
                    profit = 0

            row = {
                "symbol": s["symbol"],
                "price": s["price"] if s["price"] is not None else "",
                "signal": s["signal"],
                "target": round(s["target"], 6) if s["target"] else "",
                "stop": round(s["stop"], 6) if s["stop"] else "",
                "strategy": s.get("strategy",""),
                "confidence": s.get("confidence",0),
                "risk_reward": rr,
                "position_size": size,
                "expected_loss": expected_loss,
                "profit": round(profit, 6),
                "time": datetime.utcnow().isoformat()
            }
            log_signal(row)
            print(f"[{row['time']}] {row['symbol']} {row['signal']} via {row['strategy']} RR:{rr} size:{size} profit:{profit:.4f}")
        time.sleep(REFRESH_SECONDS)
    print("✅ تست زنده کامل شد.")

if __name__ == "__main__":
    run_forward_test()

