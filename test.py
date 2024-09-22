import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Fetch Stock Data
ticker = 'META'
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

# Step 4: Generate Buy/Sell Signals
def generate_signals(data):
    buy_signals = []
    sell_signals = []
    
    for i in range(len(data)):
        close_price = data['Close'].iloc[i]
        sma_value = data['SMA_50'].iloc[i]
        rsi_value = data['RSI_14'].iloc[i]

        if (close_price >= sma_value) and (rsi_value < 30):
            buy_signals.append(close_price)
            sell_signals.append(float('nan'))  # No sell signal
        elif (close_price <= sma_value) and (rsi_value > 70):
            sell_signals.append(close_price)
            buy_signals.append(float('nan'))  # No buy signal
        else:
            buy_signals.append(float('nan'))  # No buy signal
            sell_signals.append(float('nan'))  # No sell signal

        # Debugging output
        print(f"Date: {data.index[i]}, Close: {close_price}, SMA: {sma_value}, RSI: {rsi_value}")

    return pd.Series(buy_signals, index=data.index), pd.Series(sell_signals, index=data.index)

# Generate signals and add to the DataFrame
stock_data['Buy_Signal'], stock_data['Sell_Signal'] = generate_signals(stock_data)

# Display the last few rows to check the signals
print(stock_data[['Close', 'SMA_50', 'RSI_14', 'Buy_Signal', 'Sell_Signal']].tail(10))


# Step 5: Calculate Bollinger Bands
def calculate_bollinger_bands(data, window=20):
    # Calculate the middle band (SMA)
    data['Middle_Band'] = data['Close'].rolling(window=window).mean()
    # Calculate the standard deviation
    data['Std_Dev'] = data['Close'].rolling(window=window).std()
    # Calculate upper and lower bands
    data['Upper_Band'] = data['Middle_Band'] + (2 * data['Std_Dev'])
    data['Lower_Band'] = data['Middle_Band'] - (2 * data['Std_Dev'])

# Add Bollinger Bands to the stock data
calculate_bollinger_bands(stock_data)

# Display the last few rows to check the Bollinger Bands
print(stock_data[['Close', 'Middle_Band', 'Upper_Band', 'Lower_Band']].tail(10))


# Step 6: Visualize the Stock Price and Bollinger Bands
def plot_bollinger_bands(data):
    plt.figure(figsize=(14, 7))
    plt.plot(data['Close'], label='Close Price', color='blue', alpha=0.5)
    plt.plot(data['Middle_Band'], label='Middle Band (SMA)', color='orange', linestyle='--', alpha=0.7)
    plt.plot(data['Upper_Band'], label='Upper Band', color='green', linestyle='--', alpha=0.7)
    plt.plot(data['Lower_Band'], label='Lower Band', color='red', linestyle='--', alpha=0.7)

    plt.fill_between(data.index, data['Lower_Band'], data['Upper_Band'], color='lightgrey', alpha=0.5)
    plt.title('Bollinger Bands')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid()
    plt.tight_layout()

    # Save the plot as a PNG image
    plt.savefig('bollinger_bands.png')
    plt.show()

# Call the plotting function
plot_bollinger_bands(stock_data)

# Step 7: Calculate Stochastic Oscillator
def calculate_stochastic_oscillator(data, window=14):
    # Calculate the lowest low and highest high over the window
    lowest_low = data['Close'].rolling(window=window).min()
    highest_high = data['Close'].rolling(window=window).max()
    
    # Calculate %K
    data['%K'] = 100 * ((data['Close'] - lowest_low) / (highest_high - lowest_low))
    # Calculate %D as a 3-period SMA of %K
    data['%D'] = data['%K'].rolling(window=3).mean()

# Add Stochastic Oscillator to the stock data
calculate_stochastic_oscillator(stock_data)

# Display the last few rows to check the Stochastic Oscillator
print(stock_data[['Close', '%K', '%D']].tail(10))

# Step 8: Visualize the Stochastic Oscillator
def plot_stochastic_oscillator(data):
    plt.figure(figsize=(14, 7))
    plt.plot(data['%K'], label='%K', color='blue', alpha=0.5)
    plt.plot(data['%D'], label='%D', color='orange', alpha=0.7)

    # Adding horizontal lines for overbought and oversold levels
    plt.axhline(80, linestyle='--', alpha=0.5, color='red')
    plt.axhline(20, linestyle='--', alpha=0.5, color='green')

    plt.title('Stochastic Oscillator')
    plt.xlabel('Date')
    plt.ylabel('Stochastic Value')
    plt.legend()
    plt.grid()
    plt.tight_layout()

    # Save the plot as a PNG image
    plt.savefig('stochastic_oscillator.png')
    plt.show()

# Call the plotting function
plot_stochastic_oscillator(stock_data)


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
