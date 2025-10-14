import os
import json
import csv
import time
from collections import defaultdict, OrderedDict
import matplotlib.pyplot as plt
import shutil

def save_mix(weights, symbols, performance):
    os.makedirs("output/mixes", exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"output/mixes/saved_mix_{timestamp}.json"
    data = {
        "symbols": symbols,
        "weights": weights,
        "performance": performance
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✅ ترکیب ذخیره شد: {filename}")

RESULTS_CSV = "output/results.csv"
MIX_DIR = "output/mix"
SAVED_MIXES = os.path.join(MIX_DIR, "saved_mixes.json")

# ما یک متغیر سطح ماژول برای استفاده در بخش تولید HTML نگه می‌داریم
symbol_profits = {}

def ensure_dirs():
    os.makedirs(MIX_DIR, exist_ok=True)
    os.makedirs(os.path.dirname("output/mix_dashboard.html"), exist_ok=True)

def load_results(path=RESULTS_CSV):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Results file not found: {path}")
    symbols = defaultdict(list)
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            profit = float(r.get("Profit", 0) or 0)
            sym = r.get("Symbol", "").strip()
            symbols[sym].append(profit)
            rows.append(r)
    return symbols, rows

def cumulative(profits):
    cum = []
    s = 0.0
    for p in profits:
        s += p
        cum.append(s)
    return cum

def max_drawdown(series):
    peak = -float("inf")
    max_dd = 0.0
    for v in series:
        if v > peak:
            peak = v
        dd = peak - v
        if dd > max_dd:
            max_dd = dd
    return max_dd

def normalize_weights(weights):
    total = sum(weights.values())
    if total == 0:
        n = {k: 1.0/len(weights) for k in weights}
    else:
        n = {k: v/total for k, v in weights.items()}
    return n

def simulate_mix(symbol_profits_local, weights):
    norm = normalize_weights(weights)
    symbols = list(symbol_profits_local.keys())
    max_len = max((len(symbol_profits_local[s]) for s in symbols), default=0)
    combined = []
    for i in range(max_len):
        step = 0.0
        for s in symbols:
            vals = symbol_profits_local[s]
            v = vals[i] if i < len(vals) else 0.0
            step += norm.get(s, 0.0) * v
        combined.append(step)
    cum = cumulative(combined)
    dd = max_drawdown(cum)
    return {
        "combined_series": combined,
        "cumulative": cum,
        "total_profit": cum[-1] if cum else 0.0,
        "max_drawdown": dd,
    }

def score_mix(result):
    profit = result["total_profit"]
    dd = result["max_drawdown"]
    score = profit - 0.5 * dd
    return score

def save_mix_record(record):
    ensure_dirs()
    if os.path.exists(SAVED_MIXES):
        try:
            with open(SAVED_MIXES, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = []
    else:
        data = []
    data.append(record)
    with open(SAVED_MIXES, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def run_predefined(symbol_profits_local):
    symbols = list(symbol_profits_local.keys())
    equal = {s: 1.0 for s in symbols}
    perf = {s: sum(symbol_profits_local[s]) for s in symbols}
    pos_perf = {s: max(sum(symbol_profits_local[s]), 0.0) for s in symbols}
    mixes = OrderedDict([
        ("equal", equal),
        ("performance", perf),
        ("positive_performance", pos_perf)
    ])
    results = {}
    for name, weights in mixes.items():
        res = simulate_mix(symbol_profits_local, weights)
        res["weights"] = normalize_weights(weights)
        res["name"] = name
        res["score"] = score_mix(res)
        results[name] = res
    return results

def plot_results(all_results):
    ensure_dirs()
    plt.figure(figsize=(10,6))
    for name, res in all_results.items():
        plt.plot(res["cumulative"], label=f"{name} (P={res['total_profit']:.2f}, DD={res['max_drawdown']:.2f})", linewidth=2)
    plt.title("Mixed Strategy Cumulative Profit Comparison")
    plt.xlabel("Step Index")
    plt.ylabel("Cumulative Profit")
    plt.legend()
    plt.grid(True)
    chart_path = os.path.join(MIX_DIR, "mix_comparison.png")
    plt.savefig(chart_path)
    plt.close()
    return chart_path

def export_dashboard(symbols, default_weights, last_results, chart_path, out_html="output/mix_dashboard.html"):
    ensure_dirs()

    # ساخت ورودی‌های HTML برای هر نماد (ایمن با .format در خودِ هر خط)
    symbols_inputs_lines = []
    for s in symbols:
        v = default_weights.get(s, 0)
        symbols_inputs_lines.append(
            '<label style="display:block;margin:6px 0;"><strong>{s}</strong> <input type="number" step="0.01" name="{s}" value="{v:.4f}" style="width:120px;"></label>'.format(s=s, v=v)
        )
    symbols_inputs = "\n".join(symbols_inputs_lines)

    # آماده‌سازی داده‌های جاوااسکریپت (JSON) به عنوان رشته
    js_data = json.dumps({s: symbol_profits.get(s, []) for s in symbols}, ensure_ascii=False)

    # قالب HTML با placeholder های مشخص برای جایگذاری بعدی
    html_template = """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Mix Dashboard</title>
  <style>
    body { font-family: sans-serif; padding:20px; background:#f6f7fb; }
    .controls { background:#fff; padding:12px; border:1px solid #ddd; display:inline-block; vertical-align:top; }
    .output { display:inline-block; margin-left:20px; vertical-align:top; }
    button { margin-top:8px; padding:8px 12px; }
    .warning { background:#fff3cd; padding:10px; border:1px solid #ffeeba; }
  </style>
</head>
<body>
  <h1>Mix Dashboard</h1>
  <div class="controls">
    <h3>Weights</h3>
    <form id="weightsForm">
      __SYMBOLS_INPUTS__
      <div>
        <button type="button" onclick="computeMix()">محاسبه ترکیب</button>
        <button type="button" onclick="saveMix()">ذخیره ترکیب</button>
        <button type="button" onclick="saveMixServer()">ذخیره سروری</button>
      </div>
    </form>
  </div>
  <div class="output">
    <h3>نتایج</h3>
    <div id="summary"></div>
    <img id="chart" src="__CHART_NAME__" style="max-width:600px;border:1px solid #ccc;">
  </div>
  <script>
  const symbolData = __JSDATA__;
  function cumulative(arr){ let s=0; return arr.map(function(v){ s += v; return s; }); }
  function maxDrawdown(series){ var peak=-Infinity, m=0; for(var i=0;i<series.length;i++){ var v=series[i]; if(v>peak) peak=v; var d=peak-v; if(d>m) m=d; } return m; }
  function computeMix(){
    var form = document.getElementById('weightsForm');
    var fd = new FormData(form);
    var weights = {};
    var total = 0;
    for(var pair of fd.entries()){ var k=pair[0], v=parseFloat(pair[1])||0; weights[k]=v; total += Math.abs(v); }
    if(total===0){ for(var k in weights) weights[k]=1; total=Object.keys(weights).length; }
    for(var k in weights) weights[k] = weights[k]/total;
    var symbols = Object.keys(symbolData);
    var maxLen = 0;
    for(var i=0;i<symbols.length;i++){ if(symbolData[symbols[i]].length > maxLen) maxLen = symbolData[symbols[i]].length; }
    var comb = [];
    for(var i=0;i<maxLen;i++){
      var step = 0;
      for(var si=0; si<symbols.length; si++){
        var s = symbols[si];
        var v = (symbolData[s][i] !== undefined) ? symbolData[s][i] : 0;
        step += (weights[s] || 0) * v;
      }
      comb.push(step);
    }
    var cum = cumulative(comb);
    var profit = cum.length ? cum[cum.length-1] : 0;
    var dd = maxDrawdown(cum);
    document.getElementById('summary').innerHTML = '<div><strong>Total Profit</strong>: ' + profit.toFixed(4) + ' &nbsp; <strong>Max Drawdown</strong>: ' + dd.toFixed(4) + '</div>';
  }
  function saveMix(){
    var form = document.getElementById('weightsForm');
    var fd = new FormData(form);
    var mix = {};
    for(var pair of fd.entries()){ mix[pair[0]] = parseFloat(pair[1])||0; }
    var saved = JSON.parse(localStorage.getItem('saved_mixes')||'[]');
    saved.push({timestamp: Date.now(), weights: mix});
    localStorage.setItem('saved_mixes', JSON.stringify(saved));
    alert('ترکیب در localStorage ذخیره شد. برای ذخیره سروری، از دکمه ذخیره سروری استفاده کنید.');
  }
  function saveMixServer(){
    var form = document.getElementById('weightsForm');
    var fd = new FormData(form);
    var payload = {};
    for(var pair of fd.entries()){ payload[pair[0]] = parseFloat(pair[1])||0; }
    fetch('save_mix', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({timestamp: Date.now(), weights: payload}) })
      .then(function(r){ return r.json(); })
      .then(function(j){ alert('Server saved: ' + (j.ok? 'OK' : JSON.stringify(j))); })
      .catch(function(e){ alert('Server save failed: ' + e); });
  }
  </script>
</body>
</html>
"""

    # جایگزینی محتوا با متد replace (ایمن در برابر آکولادهای JS)
    chart_name = os.path.basename(chart_path)
    html_content = html_template.replace("__SYMBOLS_INPUTS__", symbols_inputs)
    html_content = html_content.replace("__CHART_NAME__", chart_name)
    html_content = html_content.replace("__JSDATA__", js_data)

    # نوشتن فایل HTML و کپی کردن تصویر به همان دایرکتوری برای بارگذاری نسبی
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    try:
        shutil.copy(chart_path, os.path.join(os.path.dirname(out_html), chart_name))
    except Exception:
        pass

    return out_html


def run_all(save_threshold_score=5.0):
    ensure_dirs()
    global symbol_profits
    symbol_profits, rows = load_results()
    results = run_predefined(symbol_profits)
    chart_path = plot_results(results)
    for name, res in results.items():
        if res["score"] >= save_threshold_score:
            record = {
                "name": name,
                "weights": res["weights"],
                "total_profit": res["total_profit"],
                "max_drawdown": res["max_drawdown"],
                "score": res["score"]
            }
            save_mix_record(record)
    symbols = list(symbol_profits.keys())
    default_weights = {s: 1.0 for s in symbols}
    out_html = export_dashboard(symbols, default_weights, results, chart_path)
    print("✅ Mix run completed. Dashboard:", out_html)
    print("✅ Saved mixes file:", SAVED_MIXES)
    return results

if __name__ == "__main__":
    try:
        run_all(save_threshold_score=5.0)
    except Exception as e:
        print("Error running strategy_mixer:", e)

