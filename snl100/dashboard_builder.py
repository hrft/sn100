import os
import csv
from collections import defaultdict


def build_dashboard_html(results_file="output/results.csv", output_file="output/dashboard.html"):
    print("🔍 Checking for results file:", results_file)
    print("🔍 File exists?", os.path.exists(results_file))

    html = """
    <html>
    <head>
        <title>Signal Dashboard</title>
        <style>
            body { font-family: sans-serif; padding: 20px; background: #f4f4f4; }
            h1 { color: #333; }
            input { margin-bottom: 10px; padding: 5px; width: 300px; }
            table { border-collapse: collapse; width: 100%; background: #fff; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }
            th { background: #eee; cursor: pointer; }
            tr:hover { background: #f9f9f9; }
            .hit_target { background-color: #d4edda; }
            .hit_stop { background-color: #f8d7da; }
            .neutral { background-color: #e2e3e5; }
            .profit-total-positive { background-color: #c6f6d5; font-weight: bold; }
            .profit-total-negative { background-color: #fbb6ce; font-weight: bold; }
            .warning { background: #fff3cd; padding: 20px; border: 1px solid #ffeeba; color: #856404; margin-bottom: 20px; }
            .chart-container { margin-top: 40px; }
        </style>
        <script>
            function sortTable(n) {
                var table = document.getElementById("signalTable");
                var rows = Array.from(table.rows).slice(1);
                var asc = table.getAttribute("data-sort-dir") !== "asc";
                rows.sort(function(a, b) {
                    var x = a.cells[n].innerText;
                    var y = b.cells[n].innerText;
                    return asc ? x.localeCompare(y, undefined, {numeric: true}) : y.localeCompare(x, undefined, {numeric: true});
                });
                rows.forEach(row => table.appendChild(row));
                table.setAttribute("data-sort-dir", asc ? "asc" : "desc");
            }

            function filterTable() {
                var input = document.getElementById("filterInput").value.toUpperCase();
                var table = document.getElementById("signalTable");
                var tr = table.getElementsByTagName("tr");
                for (var i = 1; i < tr.length; i++) {
                    var txt = tr[i].innerText.toUpperCase();
                    tr[i].style.display = txt.includes(input) ? "" : "none";
                }
            }
        </script>
    </head>
    <body>
        <h1>Signal Dashboard</h1>
    """

    if not os.path.exists(results_file):
        html += """
        <div class="warning">
            ⚠️ No results available yet.<br>
            Please run <code>signal_executor.py</code> to generate <code>results.csv</code>.
        </div>
        </body></html>
        """
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"⚠️ فایل {results_file} پیدا نشد. داشبورد خالی ساخته شد: {output_file}")
        return

    rows = []
    total_profit = 0.0
    symbol_profits = defaultdict(list)

    with open(results_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            profit = float(row.get("Profit", 0))
            total_profit += profit
            rows.append(row)
            symbol = row.get("Symbol", "")
            symbol_profits[symbol].append(profit)

    html += """
        <input type="text" id="filterInput" onkeyup="filterTable()" placeholder="🔍 Filter by symbol, result, profit...">
        <table id="signalTable" data-sort-dir="asc">
            <tr>
                <th onclick="sortTable(0)">Time</th>
                <th onclick="sortTable(1)">Symbol</th>
                <th onclick="sortTable(2)">Signal</th>
                <th onclick="sortTable(3)">Entry</th>
                <th onclick="sortTable(4)">Stop</th>
                <th onclick="sortTable(5)">Target</th>
                <th onclick="sortTable(6)">Result</th>
                <th onclick="sortTable(7)">Profit</th>
                <th>Chart</th>
            </tr>
    """

    for row in rows:
        result = row.get("Result", "").strip()
        css_class = result if result in ["hit_target", "hit_stop", "neutral"] else ""
        html += f"""
            <tr class="{css_class}">
                <td>{row.get("Time", "")}</td>
                <td>{row.get("Symbol", "")}</td>
                <td>{row.get("Signal", "entry")}</td>
                <td>{row.get("Entry", "")}</td>
                <td>{row.get("Stop", "")}</td>
                <td>{row.get("Target", "")}</td>
                <td>{result}</td>
                <td>{row.get("Profit", "")}</td>
                <td><a href="signals/{row.get("Symbol", "")}_chart.html" target="_blank">View</a></td>
            </tr>
        """

    css_total = "profit-total-positive" if total_profit >= 0 else "profit-total-negative"
    html += f"""
        <tr>
            <td colspan="7" style="text-align:right;"><strong>Total Profit:</strong></td>
            <td class="{css_total}">{round(total_profit, 4)}</td>
            <td></td>
        </tr>
        </table>
    """

    if not os.path.exists("output/symbol_summary.csv"):
        html += "<div class='warning'>⚠️ خلاصه‌ی نمادها هنوز آماده نیست. لطفاً performance_analyzer.py را اجرا کنید.</div>"

    if not os.path.exists("output/overall_summary.csv"):
        html += "<div class='warning'>⚠️ خلاصه‌ی کلی هنوز تولید نشده. لطفاً performance_analyzer.py را اجرا کنید.</div>"

    html += '<div class="chart-container">'
    for symbol in symbol_profits:
        chart_path = f"charts/{symbol}_cumulative.png"
        if os.path.exists(f"output/{chart_path}"):
            html += f"""
                <h2>{symbol} – Cumulative Profit</h2>
                <img src="{chart_path}" alt="{symbol} cumulative chart" style="max-width: 100%; border: 1px solid #ccc; margin-bottom: 30px;">
            """
    html += "</div></body></html>"

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ داشبورد نهایی با بررسی کامل فایل‌ها ساخته شد: {output_file}")

if __name__ == "__main__":
    build_dashboard_html()

