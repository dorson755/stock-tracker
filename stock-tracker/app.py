from flask import Flask, render_template, request, redirect, url_for
import yfinance as yf
import plotly.graph_objs as go
import plotly.io as pio

app = Flask(__name__)

# Route to handle stock search form
@app.route('/search_stock', methods=['POST'])
def search_stock():
    symbol = request.form.get('symbol').upper()  # Get stock symbol from form
    return redirect(url_for('show_stock', symbol=symbol))

@app.route('/stocks/<symbol>', methods=['GET'])
def show_stock(symbol):
    # Fetch live data for the stock
    stock = yf.Ticker(symbol)
    data = stock.history(period='5d')  # Get the last 5 days' data for better visualization

    if data.empty:
        return f"No live data found for {symbol}. Please check the stock symbol."

    # Create a Plotly graph
    fig = go.Figure()

    # Add candlestick chart for the stock price
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='Stock Price'
    ))

    # Set chart title and labels
    fig.update_layout(
        title=f'Live Stock Data for {symbol}',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False
    )

    # Convert Plotly graph to JSON for rendering in HTML
    graph_json = pio.to_json(fig)

    return render_template('plotly_chart.html', graph_json=graph_json)

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
