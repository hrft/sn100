from flask import Flask, render_template_string
import pandas as pd
import os
from snl100.config import OUTPUT_LOG, DASHBOARD_PORT

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Live Signal Dashboard (USDT)</title>
  <meta http-equiv="refresh" content="5">
  <style>
    body { font-family: sans-serif; padding: 20px; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ccc; padding: 6px; text-align: center; }
    th { background: #eee; }
    .buy { background: #d4f8d4; }
    .sell { background: #f8d4d4; }
    .hold { background: #f8f4d4; }
  </style>
</head>
<body>
  <h2>📡 داشبورد سیگنال زنده (USDT)</h2>
  {% if df is none %}
    <p>هنوز داده‌ای ثبت نشده.</p>
  {% else %}
  <table>
    <tr>
      {% for col in df.columns %}
      <th>{{ col }}</th>
      {% endfor %}
    </tr>
    {% for _, row in df.iterrows() %}
    <tr class="{{ row['signal'] }}">
      {% for col in df.columns %}
      <td>{{ row[col] }}</td>
      {% endfor %}
    </tr>
    {% endfor %}
  </table>
  {% endif %}
</body>
</html>
"""

@app.route("/")
def dashboard():
    if not os.path.exists(OUTPUT_LOG):
        return render_template_string(TEMPLATE, df=None)
    df = pd.read_csv(OUTPUT_LOG)
    cols = ["symbol","price","signal","target","stop","strategy","confidence",
            "risk_reward","position_size","expected_loss","profit","time"]
    df = df[[c for c in cols if c in df.columns]].sort_values("time", ascending=False).head(50)
    return render_template_string(TEMPLATE, df=df)

if __name__ == "__main__":
    app.run(debug=True, port=DASHBOARD_PORT)

