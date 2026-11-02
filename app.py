import os
import sqlite3
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "taskpaybd_secure_secret_key"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "arefinhossain345@gmail.com"
SENDER_PASSWORD = "kqas kdcq lvua peml"

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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS temp_users (
            email TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            otp TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS withdraws (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            method TEXT NOT NULL,
            number TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'Pending'
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def send_otp_email(receiver_email, otp_code):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = "TaskPayBD - OTP Code"
        msg.attach(MIMEText(f"Apnar OTP code holo: {otp_code}", 'plain'))
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False

LAYOUT = '''
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TaskPayBD</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background-color: #070d1b; color: #ffffff; font-family: sans-serif; }
        .navbar { background: #070d1b; border-bottom: 1px solid #1c2541; padding: 15px 30px; }
        .brand-logo { font-weight: 800; font-size: 24px; color: #22c55e; text-decoration: none; }
        .btn-green { background-color: #16a34a; color: white; font-weight: 600; border-radius: 6px; padding: 8px 20px; text-decoration: none; }
        .btn-green:hover { background-color: #15803d; color: white; }
        .main-card { background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 30px; max-width: 500px; margin: 40px auto; }
        .form-control, .form-select { background-color: #030712; border: 1px solid #374151; color: white; padding: 12px; border-radius: 8px; }
        .form-control:focus, .form-select:focus { background-color: #030712; color: white; border-color: #22c55e; box-shadow: none; }
        .feature-card { background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 25px; height: 100%; }
        .footer-section { background-color: #040812; color: #9ca3af; padding: 30px 0; border-top: 1px solid #1f2937; font-size: 14px; text-align: center; margin-top: 50px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="brand-logo" href="/">TaskPayBD</a>
            <div>
                <a class="text-white text-decoration-none me-3" href="/">হোম</a>
                <a class="text-white text-decoration-none me-3" href="/surveys">Surveys</a>
                <a class="text-white text-decoration-none me-3" href="/terms">Terms</a>
                {% if 'user' in session %}
                    <a href="/dashboard" class="btn btn-outline-success btn-sm me-2">ড্যাশবোর্ড</a>
                    <a href="/logout" class="btn btn-outline-danger btn-sm">লগ আউট</a>
                {% else %}
                    <a href="/login" class="btn btn-outline-success btn-sm me-2">লগ ইন</a>
                    <a href="/signup" class="btn btn-green btn-sm">রেজিস্ট্রেশন</a>
                {% endif %}
            </div>
        </div>
    </nav>
    <div class="container my-4">
        {{ content | safe }}
    </div>
    <div class="footer-section">
        &copy; 2026 TaskPayBD. All rights reserved.
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    content = '''
        <div class="text-center py-5">
            <h1 class="fw-bold text-success mb-3">পেইড সার্ভে করে আয় করুন</h1>
            <p class="text-light mb-4">TaskPayBD প্ল্যাটফর্মে সহজে অনলাইন সার্ভে করে প্রতিদিন ইনকাম করুন।</p>
            <div class="row g-4 mt-4 justify-content-center">
                <div class="col-md-4">
                    <div class="feature-card text-start">
                        <h5 class="fw-bold text-success mb-2">⏱️ দ্রুত সার্ভে</h5>
                        <p class="small text-white mb-0">সহজ সার্ভে সম্পন্ন করে দ্রুত টাকা অর্জন করুন।</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="feature-card text-start">
                        <h5 class="fw-bold text-success mb-2">💳 তাৎক্ষণিক ক্যাশআউট</h5>
                        <p class="small text-white mb-0">বিকাশ এবং নগদের মাধ্যমে আপনার টাকা তুলে নিন।</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="feature-card text-start">
                        <h5 class="fw-bold text-success mb-2">👤 ১০০% ফ্রি রেজিস্ট্রেশন</h5>
                        <p class="small text-white mb-0">কোনো খরচ ছাড়াই আজই আপনার অ্যাকাউন্ট তৈরি করুন।</p>
                    </div>
                </div>
            </div>
            <div class="mt-5">
                <a href="/signup" class="btn btn-green btn-lg rounded-pill px-5">এখনই ফ্রি অ্যাকাউন্ট খুলুন</a>
            </div>
        </div>
    '''
    return render_template_string(LAYOUT, content=content)

@app.route('/surveys')
def surveys():
    content = '''
        <div class="main-card" style="max-width:800px;">
            <h3 class="text-success fw-bold mb-3">All Available Surveys</h3>
            <p class="text-light small mb-4">নিচের সার্ভে বক্সে ক্লিক করে কাজ শুরু করুন:</p>
            <div class="p-4 bg-dark rounded border border-success text-center">
                <h5 class="text-white fw-bold mb-2">CPX Research & BitLabs Survey Wall</h5>
                <p class="small text-muted mb-3">এখানে সমস্ত লাইভ সার্ভে একসাথে লোড হবে।</p>
                <button class="btn btn-green px-4 py-2" onclick="alert('Survey loading...')">সার্ভে লোড করুন</button>
            </div>
        </div>
    '''
    return render_template_string(LAYOUT, content=content)

@app.route('/terms')
def terms():
    content = '''
        <div class="main-card" style="max-width:800px;">
            <h3 class="text-success fw-bold mb-3">Terms & Conditions (শর্তাবলী)</h3>
            <p class="text-light small">১. প্রতি ব্যবহারকারী শুধুমাত্র একটি অ্যাকাউন্ট খুলতে পারবেন। একাধিক অ্যাকাউন্ট তৈরি সম্পূর্ণ নিষিদ্ধ।<br>
            ২. ভিপিএন (VPN) বা বট ব্যবহার করলে অ্যাকাউন্ট সাথে সাথে ব্যান করা হবে।<br>
            ৩. ন্যূনতম উইথড্র পরিমাণ ১০০.০০ BDT (৳১০০)। বিকাশ বা নগদের মাধ্যমে পেমেন্ট দেওয়া হয়।<br>
            ৪. সঠিক তথ্য দিয়ে সার্ভে সম্পন্ন করতে হবে।</p>
        </div>
    '''
    return render_template_string(LAYOUT, content=content)

@app.route('/about')
def about():
    content = '<div class="main-card text-center"><h3 class="text-success fw-bold">About Us</h3><p class="text-light">TaskPayBD হলো বাংলাদেশের একটি বিশ্বস্ত পেইড সার্ভে প্ল্যাটফর্ম।</p></div>'
    return render_template_string(LAYOUT, content=content)

@app.route('/contact')
def contact():
    content = '<div class="main-card text-center"><h3 class="text-success fw-bold">Contact Us</h3><p class="text-light">ইমেইল: arefinhossain345@gmail.com</p></div>'
    return render_template_string(LAYOUT, content=content)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            error = "পাসওয়ার্ড মিলছে না!"
        else:
            try:
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
                if cursor.fetchone():
                    error = "এই ইমেইল ইতিমধ্যে রেজিস্টার্ড!"
                else:
                    otp = str(random.randint(100000, 999999))
                    cursor.execute("INSERT OR REPLACE INTO temp_users (email, password, otp) VALUES (?, ?, ?)", (email, password, otp))
                    conn.commit()
                    conn.close()
                    if send_otp_email(email, otp):
                        session['pending_email'] = email
                        return redirect(url_for('verify_otp'))
                    else:
                        error = "OTP পাঠাতে সমস্যা হয়েছে।"
            except Exception as e:
                error = f"Error: {e}"

    content = f'''
        <div class="main-card">
            <h3 class="text-success fw-bold mb-3 text-center">রেজিস্ট্রেশন করুন</h3>
            {f'<div class="alert alert-danger py-2">{error}</div>' if error else ''}
            <form method="POST">
                <div class="mb-3">
                    <input type="email" class="form-control" name="email" required placeholder="ই-মেইল">
                </div>
                <div class="mb-3">
                    <input type="password" class="form-control" name="password" required placeholder="পাসওয়ার্ড">
                </div>
                <div class="mb-3">
                    <input type="password" class="form-control" name="confirm_password" required placeholder="পাসওয়ার্ড নিশ্চিত করুন">
                </div>
                <button type="submit" class="btn btn-green w-100">ওটিপি পাঠান</button>
            </form>
            <p class="text-center mt-3 small text-white">একাউন্ট আছে? <a href="/login" class="text-success fw-bold">লগ ইন করুন</a></p>
        </div>
    '''
    return render_template_string(LAYOUT, content=content)

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    error = ""
    email = session.get('pending_email')
    if not email:
        return redirect(url_for('signup'))
    if request.method == 'POST':
        user_otp = request.form['otp']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT password, otp FROM temp_users WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row and row[1] == user_otp:
            cursor.execute("INSERT INTO users (email, password, balance) VALUES (?, ?, 0.0)", (email, row[0]))
            cursor.execute("DELETE FROM temp_users WHERE email = ?", (email,))
            conn.commit()
            conn.close()
            session.pop('pending_email', None)
            session['user'] = email
            return redirect(url_for('dashboard'))
        else:
            error = "ভুল OTP কোড!"
        conn.close()

    content = f'''
        <div class="main-card text-center">
            <h3 class="text-success fw-bold mb-3">ইমেইল ভেরিফিকেশন</h3>
            <p class="small text-light">আপনার জিমেইলে পাঠানো ৬ ডিজিটের OTP কোডটি দিন।</p>
            {f'<div class="alert alert-danger py-2">{error}</div>' if error else ''}
            <form method="POST">
                <div class="mb-3">
                    <input type="text" class="form-control text-center fs-4" name="otp" required maxlength="6" placeholder="------">
                </div>
                <button type="submit" class="btn btn-green w-100">ভেরিফাই করুন</button>
            </form>
        </div>
    '''
    return render_template_string(LAYOUT, content=content)

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
            error = "ভুল ইমেইল বা পাসওয়ার্ড!"

    content = f'''
        <div class="main-card">
            <h3 class="text-success fw-bold mb-3 text-center">লগ ইন করুন</h3>
            {f'<div class="alert alert-danger py-2">{error}</div>' if error else ''}
            <form method="POST">
                <div class="mb-3">
                    <input type="email" class="form-control" name="email" required placeholder="ই-মেইল">
                </div>
                <div class="mb-3">
                    <input type="password" class="form-control" name="password" required placeholder="পাসওয়ার্ড">
                </div>
                <button type="submit" class="btn btn-green w-100">লগ ইন</button>
            </form>
            <p class="text-center mt-3 small text-white">একাউন্ট নেই? <a href="/signup" class="text-success fw-bold">রেজিস্ট্রেশন করুন</a></p>
        </div>
    '''
    return render_template_string(LAYOUT, content=content)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    user_email = session['user']
    message, error = "", ""

    if request.method == 'POST':
        method = request.form['method']
        number = request.form['number']
        try:
            amount = float(request.form['amount'])
        except:
            amount = 0.0

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE email = ?", (user_email,))
        row = cursor.fetchone()
        balance = row[0] if row else 0.0

        if amount < 100.0:
            error = "সর্বনিম্ন উইথড্র পরিমাণ ১০০.০০ BDT!"
        elif amount > balance:
            error = "পর্যাপ্ত ব্যালেন্স নেই!"
        else:
            new_bal = balance - amount
            cursor.execute("UPDATE users SET balance = ? WHERE email = ?", (new_bal, user_email))
            cursor.execute("INSERT INTO withdraws (email, method, number, amount, status) VALUES (?, ?, ?, ?, 'Pending')",
                           (user_email, method, number, amount))
            conn.commit()
            message = "উইথড্র রিকোয়েস্ট সফলভাবে জমা হয়েছে!"
        conn.close()

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE email = ?", (user_email,))
    bal_row = cursor.fetchone()
    cursor.execute("SELECT method, number, amount, status FROM withdraws WHERE email = ? ORDER BY id DESC", (user_email,))
    history = cursor.fetchall()
    conn.close()

    balance = bal_row[0] if bal_row else 0.0
    history_html = "".join([f"<tr><td>{w[0]}</td><td>{w[1]}</td><td>৳{w[2]:.2f}</td><td><span class='badge bg-warning text-dark'>{w[3]}</span></td></tr>" for w in history])

    content = f'''
        <div class="row">
            <div class="col-md-4 mb-3">
                <div class="main-card text-center" style="max-width:100%;">
                    <h5 class="text-light">ব্যালেন্স</h5>
                    <h2 class="text-success fw-bold mb-3">৳{balance:.2f} BDT</h2>
                    <hr class="border-secondary">
                    <h6 class="text-light mb-3">টাকা তুলুন (বিকাশ/নগদ)</h6>
                    {f'<div class="alert alert-success py-1 small">{message}</div>' if message else ''}
                    {f'<div class="alert alert-danger py-1 small">{error}</div>' if error else ''}
                    <form method="POST">
                        <div class="mb-2 text-start">
                            <select class="form-select" name="method" required>
                                <option value="Bkash">বিকাশ (Bkash)</option>
                                <option value="Nagad">নগদ (Nagad)</option>
                            </select>
                        </div>
                        <div class="mb-2 text-start">
                            <input type="text" class="form-control" name="number" required placeholder="নম্বর (01XXXXXXXXX)">
                        </div>
                        <div class="mb-3 text-start">
                            <input type="number" class="form-control" name="amount" required placeholder="পরিমাণ (কমপক্ষে ১০০ BDT)">
                        </div>
                        <button type="submit" class="btn btn-green w-100">উইথড্র রিকোয়েস্ট</button>
                    </form>
                </div>
            </div>
            <div class="col-md-8">
                <div class="main-card mb-3" style="max-width:100%;">
                    <h5 class="text-success fw-bold mb-2">উপলব্ধ সার্ভে বক্স</h5>
                    <p class="small text-light">নিচের বাটনে ক্লিক করে অফারওয়ালের লাইভ সার্ভে সম্পন্ন করুন।</p>
                    <a href="/surveys" class="btn btn-green btn-sm">সার্ভে শুরু করুন</a>
                </div>
                <div class="main-card" style="max-width:100%;">
                    <h5 class="text-light mb-3">উইথড্র হিস্ট্রি</h5>
                    <table class="table table-dark table-striped table-bordered small text-center">
                        <thead><tr><th>মেথড</th><th>নম্বর</th><th>টাকা</th><th>স্ট্যাটাস</th></tr></thead>
                        <tbody>{history_html if history_html else '<tr><td colspan="4" class="text-muted">কোনো রেকর্ড নেই</td></tr>'}</tbody>
                    </table>
                </div>
            </div>
        </div>
    '''
    return render_template_string(LAYOUT, content=content)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
