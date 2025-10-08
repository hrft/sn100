import sys
import os
import dotenv
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
dotenv.load_dotenv()
from snl100.data_loader import generate_sample_data
from snl100.signal_engine import generate_signal
from snl100.plotter import plot_signal
from snl100.utils import save_signal_to_csv



# تولید داده تستی
df = generate_sample_data("up", 60)

# تولید سیگنال
signal = generate_signal(df)

# رسم نمودار و ذخیره خروجی HTML
plot_signal(df, signal, symbol="BTCUSDT", output_path="output/signal_chart.html")
save_signal_to_csv(signal, symbol="BTCUSDT")
