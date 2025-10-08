import pandas as pd
import os

def build_dashboard_html(signal_dir="output/signals", chart_dir="output", output_file="output/dashboard.html"):
    rows = []
    for file in os.listdir(signal_dir):
        if file.endswith("_signal.csv"):
            df = pd.read_csv(os.path.join(signal_dir, file))
            latest = df.iloc[-1]
            symbol = latest["symbol"]
            chart_link = f"{symbol}_chart.html"
            rows.append(f"""
                <tr>
                    <td>{latest['time']}</td>
                    <td>{symbol}</td>
                    <td>{latest['signal']}</td>
                    <td>{latest['entry']}</td>
                    <td>{latest['stop']}</td>
                    <td>{latest['target']}</td>
                    <td><a href="{chart_link}" target="_blank">📈 View</a></td>
                </tr>
            """)

    html = f"""
    <html>
    <head><title>SNL100 Dashboard</title></head>
    <body>
        <h2>📊 Signal Dashboard</h2>
        <table border="1" cellpadding="5">
            <tr>
                <th>Time</th><th>Symbol</th><th>Signal</th><th>Entry</th><th>Stop</th><th>Target</th><th>Chart</th>
            </tr>
            {''.join(rows)}
        </table>
    </body>
    </html>
    """

    with open(output_file, "w") as f:
        f.write(html)
    print(f"✅ داشبورد ساخته شد: {output_file}")

