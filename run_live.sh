#!/bin/bash
echo "🚀 Starting snl100 LIVE pipeline (USDT pairs)..."

export PYTHONPATH=.

mkdir -p output data

# داشبورد را در پس‌زمینه بالا بیاور
echo "📊 Starting live dashboard at http://127.0.0.1:5050 ..."
nohup python snl100/live_signal_dashboard.py > output/dashboard.log 2>&1 &

# تست زنده با auto-restart
echo "🔍 Running forward tester with auto-restart..."
while true
do
    python snl100/forward_tester.py
    echo "⚠️ forward_tester exited. Restarting in 5 seconds..."
    sleep 5
done

