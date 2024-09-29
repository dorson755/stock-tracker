from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import yfinance as yf
import plotly.graph_objs as go
import plotly.io as pio
import os
import tweepy
from dotenv import load_dotenv
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a random secret key
load_dotenv()  # Load environment variables from .env file

# Configuring SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stock_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# User Model with a separate table for favorite stocks
class FavoriteStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    favorite_stocks = db.relationship('FavoriteStock', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Initialize the database and create tables
with app.app_context():
    db.drop_all()  # WARNING: This will delete all data in the database
    db.create_all()  # Create the new tables

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def get_latest_price(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period='1d')
    return data['Close'].iloc[-1] if not data.empty else None

def get_stock_data(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period='5d')
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='Stock Price'
    ))
    return pio.to_json(fig)


# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if the user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('register'))
        
        # Create new user
        new_user = User(username=username)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()  # Get user by username
        
        # Use the check_password method for validation
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))  # Redirect to dashboard instead of home
        else:
            flash('Login failed. Check your credentials.', 'error')
    return render_template('login.html')


# Initialize Tweepy
def get_twitter_api():
    auth = tweepy.OAuth1UserHandler(
        os.getenv('TWITTER_API_KEY'),
        os.getenv('TWITTER_API_SECRET_KEY'),
        os.getenv('TWITTER_ACCESS_TOKEN'),
        os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
        os.getenv('TWITTER_BEARER_TOKEN')
    )
    return tweepy.API(auth)


# Function to fetch Bloomberg's latest tweets using Twitter API v2
def get_bloomberg_twitter_feeds():
    api = get_twitter_api()
    try:
        # Get Bloomberg's user ID (you can replace this with another user if needed)
        bloomberg_user = api.get_user(username='business')
        user_id = bloomberg_user.data.id
        
        # Fetch the latest 5 tweets
        response = api.get_users_tweets(id=user_id, max_results=5, tweet_fields=['created_at', 'text'])
        tweets = [{'text': tweet.text, 'created_at': tweet.created_at} for tweet in response.data]
        return tweets
    except Exception as e:
        print(f"Error fetching tweets: {e}")
        return []



@app.route('/dashboard')
@login_required
def dashboard():
    favorite_stocks = FavoriteStock.query.filter_by(user_id=current_user.id).all()
    twitter_feeds = get_bloomberg_twitter_feeds()  # Fetch Twitter feeds
    return render_template('dashboard.html', favorite_stocks=favorite_stocks, twitter_feeds=twitter_feeds)

# Route and function for news
def get_stock_news():
    api_key = os.getenv('NEWS_API_KEY')
    url = f"https://newsapi.org/v2/everything?q=stocks&apiKey={api_key}"
    response = requests.get(url)
    return response.json()['articles']

@app.route('/news')
def news():
    stock_news = get_stock_news()  # Get stock news from API
    return render_template('news.html', stock_news=stock_news)

# Route to handle stock search form
@app.route('/search_stock', methods=['POST'])
@login_required
def search_stock():
    symbol = request.form.get('symbol').upper()  # Get stock symbol from form
    return redirect(url_for('show_stock', symbol=symbol))

@app.route('/stocks/<symbol>', methods=['GET'])
@login_required
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

    return render_template('plotly_chart.html', graph_json=graph_json, symbol=symbol)  # Pass the symbol here


# Route for logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
