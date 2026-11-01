import os
import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "super_secret_free_survey_key"

# ডাটাবেজ ইনিশিয়ালাইজেশন ফাংশন
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            balance REAL DEFAULT 0.00
        )
    ''')
    conn.commit()
    conn.close()

# অ্যাপ চালু হওয়ার আগেই ডাটাবেজ তৈরি করে নেওয়া
init_db()

# সাধারণ এবং সুন্দর ডিজাইন স্টাইল (CSS)
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TaskPayBD - Global Survey & Earn</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f7f6; margin: 0; padding: 0; }
        header { background: #2c3e50; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        header h1 { margin: 0; font-size: 24px; }
        header nav a { color: white; text-decoration: none; margin-left: 15px; font-weight: bold; }
        header nav a:hover { text-decoration: underline; }
        .container { max-width: 600px; margin: 50px auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); }
        h2, h3 { color: #333; }
        input[type="email"], input[type="password"] { width: 100%; padding: 10px; margin: 10px 0 20px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
        button { background: #27ae60; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; width: 100%; }
        button:hover { background: #219653; }
        .alert { color: #e74c3c; margin-bottom: 15px; }
        hr { border: 0; border-top: 1px solid #eee; margin: 20px 0; }
    </style>
</head>
<body>
    <header>
        <h1>TaskPayBD</h1>
        <nav>
            <a href="/">Home</a>
            {% if 'user' in session %}
                <a href="/dashboard">Dashboard</a>
                <a href="/logout">Logout</a>
            {% else %}
                <a href="/login">Login</a>
                <a href="/signup">Sign Up</a>
            {% endif %}
        </nav>
    </header>
    <div class="container">
        {{ content | safe }}
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    
    content = '''
        <h2>Welcome to TaskPayBD</h2>
        <p>Complete global surveys and online tasks to earn real cash rewards!</p>
        <hr>
        <p><a href="/signup"><button style="background:#2980b9;">Create Account / Sign Up</button></a></p>
        <p><a href="/login"><button style="background:#8e44ad;">Login to Dashboard</button></a></p>
    '''
    return render_template_string(BASE_TEMPLATE, content=content)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (email, password, balance) VALUES (?, ?, ?)", (email, password, 0.00))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            error = "Email already exists! Please try another one."

    content = f'''
        <h3>Create Your TaskPayBD Account</h3>
        {f'<div class="alert">{error}</div>' if error else ''}
        <form method="POST">
            <label>Email Address:</label>
            <input type="email" name="email" required>
            <label>Password:</label>
            <input type="password" name="password" required>
            <button type="submit">Sign Up</button>
        </form>
        <p>Already have an account? <a href="/login">Login here</a></p>
    '''
    return render_template_string(BASE_TEMPLATE, content=content)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0] == password:
            session['user'] = email
            return redirect(url_for('dashboard'))
        else:
            error = "Invalid Email or Password! Please try again."
            
    content = f'''
        <h3>Login to TaskPayBD</h3>
        {f'<div class="alert">{error}</div>' if error else ''}
        <form method="POST">
            <label>Email Address:</label>
            <input type="email" name="email" required>
            <label>Password:</label>
            <input type="password" name="password" required>
            <button type="submit">Login</button>
        </form>
        <p>Don't have an account? <a href="/signup">Sign Up here</a></p>
    '''
    return render_template_string(BASE_TEMPLATE, content=content)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    user_email = session['user']
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE email = ?", (user_email,))
    row = cursor.fetchone()
    conn.close()
    
    balance = row[0] if row else 0.00
    
    content = f'''
        <h2>User Dashboard</h2>
        <p><strong>Welcome,</strong> {user_email}</p>
        <p><strong>Current Balance:</strong> ${balance:.2f} USD</p>
        <hr>
        <h3>Available Surveys & Offers</h3>
        <p><em>CPX Research & BitLabs offerwalls will be integrated here soon.</em></p>
    '''
    return render_template_string(BASE_TEMPLATE, content=content)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
