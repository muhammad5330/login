from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
db = mysql.connector.connect(
    host="localhost",  # Corrected host specification
    port=3306,         # Specify the port separately
    user="root",
    password="123",
    database="flask_auth"
)
cursor = db.cursor(dictionary=True)

@app.route('/')
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('home'))
        
        return "Invalid credentials"
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            db.commit()
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            return f"Error: {err}"
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
