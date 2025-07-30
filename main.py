from flask import Flask, render_template_string
import yfinance as yf
import datetime
import time

app = Flask(__name__)

TICKERS = ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "SPY"]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Stock Drawdown Monitor</title>
<style>
  body { font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0; }
  table { border-collapse: collapse; width: 80%; margin: auto; background: white; box-shadow: 0 0 10px rgba(0,0,0,0.1);}
  th, td { padding: 12px; border: 1px solid #ccc; text-align: center; }
  th { background-color: #007acc; color: white; }
  .highlight { background-color: #ff9999; font-weight: bold; }
  caption { margin-bottom: 10px; font-size: 1.5em; }
</style>
</head>
<body>
<table>
<caption>Stock Drawdown from 12-Month High</caption>
<thead>
<tr>
<th>Ticker</th>
<th>Current Price</th>
<th>12-Month High</th>
<th>Drawdown (%)</th>
</tr>
</thead>
<tbody>
{% for stock in stocks %}
<tr class="{{ 'highlight' if stock.drawdown > 0.30 else '' }}">
<td>{{ stock.ticker }}</td>
<td>${{ stock.current_price }}</td>
<td>${{ stock.high_12m }}</td>
<td>{{ (stock.drawdown*100) | round(2) }}%</td>
</tr>
{% endfor %}
</tbody>
</table>
</body>
</html>
"""

def fetch_stock_data():
    end_date = datetime.datetime.today()
    start_date = end_date - datetime.timedelta(days=365)
    stocks_data = []

    for ticker in TICKERS:
        try:
            data = yf.download(ticker,
                               start=start_date.strftime("%Y-%m-%d"),
                               end=end_date.strftime("%Y-%m-%d"),
                               progress=False,
                               auto_adjust=False)

            if data.empty:
                print(f"No data for {ticker}")
                continue

            if data.index.tz is None:
                try:
                    data = data.tz_localize('US/Eastern')
                except Exception as e:
                    print(f"Timezone localization failed for {ticker}: {e}")

            high_12m = data['High'].max()
            current_price = data['Close'][-1] if not data['Close'].empty else None

            if current_price is None or high_12m == 0:
                continue

            drawdown = 1 - current_price / high_12m

            stocks_data.append({
                "ticker": ticker,
                "current_price": round(current_price, 2),
                "high_12m": round(high_12m, 2),
                "drawdown": drawdown
            })

            time.sleep(1)  # 减缓请求频率

        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            continue

    return stocks_data

@app.route("/")
def home():
    stocks = fetch_stock_data()
    return render_template_string(HTML_TEMPLATE, stocks=stocks)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
