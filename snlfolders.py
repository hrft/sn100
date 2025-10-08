import os

BASE = "sn100"

folders = [
    "data",
    "docs",
    "output",
    "scripts",
    f"{BASE}",
    f"{BASE}/tests"
]

files = {
    "README.md": "# sn100: Signal Engine Project\n",
    "requirements.txt": "pandas\nmatplotlib\n",
    f"{BASE}/__init__.py": "",
    f"{BASE}/signal_engine.py": "# Signal generation logic\n",
    f"{BASE}/data_loader.py": "# Load data from file or API\n",
    f"{BASE}/plotter.py": "# Plot candlestick chart\n",
    f"{BASE}/utils.py": "# Helper functions\n",
    f"{BASE}/order_executor.py": "# Optional: order execution logic\n",
    f"{BASE}/tests/__init__.py": "",
    f"{BASE}/tests/test_signal_engine.py": "# Unit tests for signal engine\n"
}

# ساخت پوشه‌ها
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# ساخت فایل‌ها
for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("✅ ساختار پروژه sn100 با موفقیت ایجاد شد.")

