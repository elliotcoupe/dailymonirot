from flask import Flask, render_template_string, jsonify
import yfinance as yf
import datetime

app = Flask(__name__)

TICKERS = ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "SPY"]

HTML = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>12个月最高点回撤</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #f7f9fc;
            color: #333;
            padding: 20px;
        }
        h2 {
            text-align: center;
            margin-bottom: 24px;
            color: #222;
        }
        table {
            width: 80%;
            margin: 0 auto;
            border-collapse: collapse;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            background-color: #fff;
            border-radius: 8px;
            overflow: hidden;
        }
        th, td {
            padding: 12px 18px;
            text-align: center;
            border-bottom: 1px solid #e1e4e8;
        }
        th {
            background-color: #0366d6;
            color: #fff;
            font-weight: 600;
            letter-spacing: 0.03em;
        }
        tr:hover {
            background-color: #f1f8ff;
        }
    </style>
</head>
<body>
    <h2>股票当前价格与12个月最高价距离</h2>
    <table id="stocks-table">
        <thead>
            <tr>
                <th>股票代码</th>
                <th>当前价格 (USD)</th>
                <th>12个月最高价 (USD)</th>
                <th>距离最高点 (%)</th>
            </tr>
        </thead>
        <tbody>
            <!-- JS填充 -->
        </tbody>
    </table>

<script>
async function fetchDataAndUpdate() {
    try {
        const res = await fetch('/api/data');
        const stocks = await res.json();

        const tbody = document.querySelector("#stocks-table tbody");
        tbody.innerHTML = '';

        stocks.forEach(stock => {
            let tr = document.createElement('tr');

            let tdTicker = document.createElement('td');
            tdTicker.textContent = stock.ticker;
            tr.appendChild(tdTicker);

            let tdPrice = document.createElement('td');
            tdPrice.textContent = stock.current_price.toFixed(2);
            tr.appendChild(tdPrice);

            let tdHigh = document.createElement('td');
            tdHigh.textContent = stock.high_12m.toFixed(2);
            tr.appendChild(tdHigh);

            let tdDrawdown = document.createElement('td');
            let drawdownPercent = (stock.drawdown * 100).toFixed(2);
            tdDrawdown.textContent = drawdownPercent + '%';

            if(stock.drawdown > 0.3){
                tdDrawdown.style.color = '#ff6600';
                tdDrawdown.style.backgroundColor = '#fff4e5';
                tdDrawdown.style.fontWeight = '700';
                tdDrawdown.style.borderRadius = '4px';
                tdDrawdown.style.padding = '2px 6px';
            } else if(stock.drawdown > 0){
                tdDrawdown.style.color = '#d73a49';
                tdDrawdown.style.fontWeight = '600';
            } else {
                tdDrawdown.style.color = '#28a745';
                tdDrawdown.style.fontWeight = '600';
            }

            tr.appendChild(tdDrawdown);
            tbody.appendChild(tr);
        });
    } catch(e) {
        console.error('更新数据失败', e);
    }
}

// 页面加载时调用一次，后续每2小时刷新
fetchDataAndUpdate();
setInterval(fetchDataAndUpdate, 2 * 60 * 60 * 1000); // 2小时毫秒数
</script>

</body>
</html>
"""

def fetch_stock_data():
    end_date = datetime.datetime.today()
    start_date = end_date - datetime.timedelta(days=365)
    stocks_data = []

    for ticker in TICKERS:
        try:
            ticker_obj = yf.Ticker(ticker)
            data = ticker_obj.history(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))
            if data.empty:
                continue

            high_12m = data['High'].max()
            current_price = data['Close'][-1] if not data['Close'].empty else None

            if current_price is None or high_12m == 0:
                continue

            drawdown = 1 - current_price / high_12m

            stocks_data.append({
                "ticker": ticker,
                "current_price": round(current_price, 2),
                "high_12m": round(high_12m, 2),
                "drawdown": round(drawdown, 4)
            })
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            continue

    return stocks_data

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/data")
def api_data():
    data = fetch_stock_data()
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
