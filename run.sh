#!/bin/bash
echo "🚀 Starting snl100 pipeline..."

export PYTHONPATH=.

echo "🔍 Step 1: Scanning symbols..."
python scripts/scan_all_v2b.py

echo "📊 Step 2: Executing signals..."
python snl100/signal_executor.py

echo "📈 Step 3: Analyzing performance..."
python snl100/performance_analyzer.py

echo "🧱 Step 4: Building dashboard..."
python snl100/dashboard_builder.py

echo "✅ All steps completed. Dashboard ready at output/dashboard.html"

