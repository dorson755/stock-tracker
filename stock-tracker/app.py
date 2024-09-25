from flask import Flask, render_template, request
import yfinance as yf
import os
import matplotlib.pyplot as plt

app = Flask(__name__)

# Directory for saving the generated plots
if not os.path.exists('static/images'):
    os.makedirs('static/images')

# Function to fetch stock data and generate the stock signals chart
def analyze_stock(symbol):
    stock_data = yf.download(symbol, period='1y', interval='1d')

    # Simple Moving Average (SMA) Calculation
    stock_data['SMA_50'] = stock_data['Close'].rolling(window=50).mean()
    
    # Bollinger Bands Calculation
    stock_data['BB_upper'] = stock_data['SMA_50'] + 2 * stock_data['Close'].rolling(window=20).std()
    stock_data['BB_lower'] = stock_data['SMA_50'] - 2 * stock_data['Close'].rolling(window=20).std()

    # Plot the stock price and SMA
    plt.figure(figsize=(14, 7))
    plt.plot(stock_data['Close'], label=f'{symbol} Close Price', color='blue', alpha=0.5)
    plt.plot(stock_data['SMA_50'], label='SMA 50', color='orange', alpha=0.8)
    plt.title(f'{symbol} Stock Price with SMA 50')
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(f'static/images/stock_price_sma.png')
    plt.close()

    # Plot Bollinger Bands
    plt.figure(figsize=(14, 7))
    plt.plot(stock_data['Close'], label=f'{symbol} Close Price', color='blue', alpha=0.5)
    plt.plot(stock_data['BB_upper'], label='Bollinger Band Upper', color='green', alpha=0.7)
    plt.plot(stock_data['BB_lower'], label='Bollinger Band Lower', color='red', alpha=0.7)
    plt.title(f'{symbol} Bollinger Bands')
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(f'static/images/bollinger_bands.png')
    plt.close()

@app.route('/', methods=['GET', 'POST'])
def home():
    symbol = "AAPL"  # Default stock symbol
    if request.method == 'POST':
        symbol = request.form['symbol']  # Get stock symbol from the form
    
    # Call stock analysis function to generate charts
    analyze_stock(symbol)
    
    return render_template('index.html', symbol=symbol)

if __name__ == '__main__':
    app.run(debug=True)
