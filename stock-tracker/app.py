from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

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
    password_hash = db.Column(db.String(100), nullable=False)
    favorite_stocks = db.Column(db.String(100))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
        
        # Check if the user exists
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login failed. Check your credentials.', 'error')
    
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
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
