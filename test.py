import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Fetch Stock Data
ticker = 'AAPL'
start_date = '2020-01-01'
end_date = '2023-01-01'
stock_data = yf.download(ticker, start=start_date, end=end_date)

# Define the Technical Indicators
def calculate_sma(data, window):
    return data['Close'].rolling(window=window).mean()

def calculate_ema(data, window):
    return data['Close'].ewm(span=window, adjust=False).mean()

def calculate_rsi(data, window=14):
    delta = data['Close'].diff(1)
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Calculate Indicators
stock_data['SMA_50'] = calculate_sma(stock_data, 50)
stock_data['EMA_50'] = calculate_ema(stock_data, 50)
stock_data['RSI_14'] = calculate_rsi(stock_data, 14)

# Visualization
fig, (ax1, ax2) = plt.subplots(2, figsize=(12, 8))

ax1.plot(stock_data.index, stock_data['Close'], label='Close Price', color='blue', lw=2)
ax1.plot(stock_data.index, stock_data['SMA_50'], label='50-day SMA', color='orange', lw=2)
ax1.plot(stock_data.index, stock_data['EMA_50'], label='50-day EMA', color='green', lw=2)
ax1.set_title(f'{ticker} Stock Price with SMA and EMA')
ax1.set_xlabel('Date')
ax1.set_ylabel('Price')
ax1.legend()

ax2.plot(stock_data.index, stock_data['RSI_14'], label='14-day RSI', color='purple', lw=2)
ax2.axhline(70, linestyle='--', alpha=0.5, color='red')  # Overbought threshold
ax2.axhline(30, linestyle='--', alpha=0.5, color='green')  # Oversold threshold
ax2.set_title(f'{ticker} 14-day RSI')
ax2.set_xlabel('Date')
ax2.set_ylabel('RSI')
ax2.legend()

# Save the plot as an image
plt.tight_layout()
plt.savefig('stock_plot.png')

# plt.show() -- (if running in an environment where a window should open)
