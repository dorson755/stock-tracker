from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
import pandas as pd

app = Flask(__name__)
CORS(app)  # Enable CORS

def calculate_indicators(data):
    # Simple Moving Average (SMA)
    data['SMA_50'] = data['Close'].rolling(window=50).mean()

    # Bollinger Bands
    data['Upper_BB'] = data['SMA_50'] + (data['Close'].rolling(window=50).std() * 2)
    data['Lower_BB'] = data['SMA_50'] - (data['Close'].rolling(window=50).std() * 2)

    # Stochastic Oscillator (using a 14-period lookback)
    high_14 = data['High'].rolling(window=14).max()
    low_14 = data['Low'].rolling(window=14).min()
    data['%K'] = 100 * ((data['Close'] - low_14) / (high_14 - low_14))
    data['%D'] = data['%K'].rolling(window=3).mean()

    # Return the modified DataFrame
    return data

@app.route('/stocks', methods=['GET'])
def get_stock_data():
    symbol = request.args.get('symbol')
    if not symbol:
        return jsonify({"error": "Symbol is required"}), 400

    try:
        # Fetch the stock data from yfinance
        stock = yf.Ticker(symbol)
        data = stock.history(period="1mo")  # Get last month's data

        # Calculate the indicators
        data = calculate_indicators(data)

        # Return the data as a JSON object, converting the index (Date) to string for JSON serialization
        data.reset_index(inplace=True)
        data['Date'] = data['Date'].astype(str)
        return jsonify(data.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
