from flask import Flask, render_template_string
import pandas as pd
import os

app = Flask(__name__)
LOG_FILE = "output/forward_test_log.csv"

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Live Signal Dashboard</title>
  <meta http-equiv="refresh" content="5">
  <style>
    body { font-family: sans-serif; padding: 20px; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }
    th { background: #eee; }
  </style>
</head>
<body>
  <h2>📡 Live Signal Dashboard</h2>
  <table>
    <tr>
      {% for col in df.columns %}
      <th>{{ col }}</th>
      {% endfor %}
    </tr>
    {% for row in df.values %}
    <tr>
      {% for val in row %}
      <td>{{ val }}</td>
      {% endfor %}
    </tr>
    {% endfor %}
  </table>
</body>
</html>
"""

@app.route("/")
def dashboard():
    if not os.path.exists(LOG_FILE):
        return "No data yet."
    df = pd.read_csv(LOG_FILE).sort_values("time", ascending=False).head(20)
    return render_template_string(TEMPLATE, df=df)

if __name__ == "__main__":
    app.run(debug=True, port=5050)

