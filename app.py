from flask import Flask, request, jsonify, session
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
from flask_cors import CORS
import requests
import os
from datetime import timedelta

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Weather API is running! Try /register or /weather"

# Configuration
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123'
app.config['MYSQL_DB'] = 'weather_app'

mysql = MySQL(app)
bcrypt = Bcrypt(app)

# User Registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE username=%s", (username,))
    if cur.fetchone():
        return jsonify({'error': 'Username already exists'}), 409

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_pw))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'User registered successfully'}), 201

# User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, password FROM users WHERE username=%s", (username,))
    user = cur.fetchone()
    cur.close()

    if user and bcrypt.check_password_hash(user[1], password):
        session['user_id'] = user[0]
        session.permanent = True
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

# Weather Data Endpoint
@app.route('/weather', methods=['GET'])
def get_weather():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    city = request.args.get('city')
    if not city:
        return jsonify({'error': 'City is required'}), 400

    api_key = os.environ.get("OPENWEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch weather data'}), response.status_code

    data = response.json()

    # Save search history
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO search_history (user_id, city) VALUES (%s, %s)", (session['user_id'], city))
    mysql.connection.commit()
    cur.close()

    return jsonify(data)

# Fetch user search history
@app.route('/history', methods=['GET'])
def get_history():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    cur = mysql.connection.cursor()
    cur.execute("SELECT city, timestamp FROM search_history WHERE user_id=%s ORDER BY timestamp DESC", (session['user_id'],))
    history = [{'city': row[0], 'timestamp': row[1].strftime('%Y-%m-%d %H:%M:%S')} for row in cur.fetchall()]
    cur.close()

    return jsonify(history)

# Logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out'})

if __name__ == '__main__':
    app.run(debug=True)
