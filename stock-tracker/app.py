from flask import Flask, render_template
import os

app = Flask(__name__)

# Home route
@app.route('/')
def home():
    return render_template('index.html', image_file="images/stock_signals.png")

if __name__ == '__main__':
    # Ensure the image is generated before running Flask
    if not os.path.exists('static/images/stock_signals.png'):
        # You can call your existing stock analysis function here to generate the plot
        pass
    app.run(debug=True)
