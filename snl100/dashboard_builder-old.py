import os
import csv
from pathlib import Path

def build_dashboard_html(output_dir="output", dashboard_file="dashboard.html"):
    signal_files = list(Path(output_dir).glob("*_signal.csv"))
    rows = []

    for file in signal_files:
        try:
            with open(file, encoding="utf-8") as f:
                reader = csv.reader(f)
                lines = list(reader)
        except Exception as e:
            print(f"⚠️ خطا در خواندن {file}: {e}")
            continue

        # اگر فایل ساختار key,value دارد
        if len(lines) > 0 and lines[0] == ["key", "value"]:
            data = dict(lines[1:])
            row = {
                "Time": data.get("Time", ""),
                "Symbol": data.get("Symbol", Path(file).stem.replace("_signal", "")),
                "Signal": data.get("Signal", data.get("strategy", "")),
                "Entry": data.get("Entry", data.get("mid_price", "")),
                "Stop": data.get("Stop", ""),
                "Target": data.get("Target", ""),
                "Chart": data.get("Chart", "")
            }
            rows.append(row)

        # اگر فایل ساختار جدولی دارد
        elif len(lines) > 0 and "Symbol" in lines[0]:
            headers = lines[0]
            for line in lines[1:]:
                row = dict(zip(headers, line))
                rows.append(row)

        else:
            print(f"⚠️ ساختار نامشخص در {file}, رد شد.")
            continue

    # ساخت HTML
    html = """
    <html>
    <head>
        <title>Signal Dashboard</title>
        <style>
            body { font-family: sans-serif; padding: 20px; background: #f4f4f4; }
            h1 { color: #333; }
            table { border-collapse: collapse; width: 100%; background: #fff; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }
            th { background: #eee; }
            tr:hover { background: #f9f9f9; }
        </style>
    </head>
    <body>
        <h1>Signal Dashboard</h1>
        <table>
            <tr>
                <th>Time</th>
                <th>Symbol</th>
                <th>Signal</th>
                <th>Entry</th>
                <th>Stop</th>
                <th>Target</th>
                <th>Chart</th>
            </tr>
    """

    for r in rows:
        html += f"""
        <tr>
            <td>{r.get('Time','')}</td>
            <td>{r.get('Symbol','')}</td>
            <td>{r.get('Signal','')}</td>
            <td>{r.get('Entry','')}</td>
            <td>{r.get('Stop','')}</td>
            <td>{r.get('Target','')}</td>
            <td><a href="{r.get('Chart','')}" target="_blank">View</a></td>
        </tr>
        """

    html += """
        </table>
    </body>
    </html>
    """

    with open(os.path.join(output_dir, dashboard_file), "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ داشبورد ساخته شد: {os.path.join(output_dir, dashboard_file)}")

