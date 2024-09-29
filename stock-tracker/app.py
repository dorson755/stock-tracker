from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import yfinance as yf
import plotly.graph_objs as go
import plotly.io as pio

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a random secret key

# Configuring SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stock_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    favorite_stocks = db.Column(db.String(100))

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Temporary code to drop the User table
with app.app_context():
    db.drop_all()  # This will drop all tables, including User and Stock
    db.create_all()  # This will recreate the tables with the updated schema


# Initialize the database
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        new_user = User(username=username, password=password)  # Hash the password in a real app
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, password=password).first()  # Password check should be hashed
        if user:
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login failed. Check your credentials.')
    return render_template('login.html')

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

    return render_template('plotly_chart.html', graph_json=graph_json)

# Route for logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
