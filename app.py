import os
import sqlite3
import random
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "taskpaybd_secure_secret_key"

# Gmail SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "arefinhossain345@gmail.com"
SENDER_PASSWORD = "kqas kdcq lvua peml"  # আপনার জেনারেট করা অ্যাপ পাসওয়ার্ড

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
        msg['Subject'] = "TaskPayBD - Email Verification OTP"
        
        body = f"আপনার TaskPayBD অ্যাকাউন্ট রেজিস্ট্রেশনের জন্য ওটিপি (OTP) কোড হলো: {otp_code}\nকোডটি কারো সাথে শেয়ার করবেন না।"
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False

def mask_email(email):
    try:
        name, domain = email.split('@')
        if len(name) <= 3:
            masked = name[0] + '***'
        else:
            masked = name[:2] + '#' * (len(name) - 3) + name[-1]
        return f"{masked}@{domain}"
    except:
        return email

BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TaskPayBD - Paid Survey Platform</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background-color: #070d1b; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .navbar { background: #070d1b; border-bottom: 1px solid #1c2541; padding: 15px 30px; }
        .brand-logo { font-weight: 800; font-size: 24px; color: #22c55e; text-decoration: none; }
        .btn-green { background-color: #16a34a; color: white; font-weight: 600; border-radius: 6px; padding: 8px 20px; text-decoration: none; }
        .btn-green:hover { background-color: #15803d; color: white; }
        .main-card { background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 30px; max-width: 500px; margin: 40px auto; }
        .form-control, .form-select { background-color: #030712; border: 1px solid #374151; color: white; padding: 12px; border-radius: 8px; }
        .form-control:focus, .form-select:focus { background-color: #030712; color: white; border-color: #22c55e; box-shadow: none; }
        .input-group-text { background-color: #030712; border: 1px solid #374151; color: #9ca3af; cursor: pointer; }
        .feature-card { background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 25px; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.3); color: #ffffff; }
        .step-box { background: #111827; border: 1px solid #1f2937; border-radius: 10px; padding: 20px; margin-top: 15px; color: #ffffff; }
        .hero-section { background: linear-gradient(180deg, #14532d 0%, #070d1b 100%); padding: 60px 20px; text-align: center; border-bottom: 2px solid #1c2541; }
        .cta-banner { background: linear-gradient(135deg, #14532d 0%, #166534 100%); border-radius: 12px; padding: 40px; margin: 50px 0; text-align: center; border: 1px solid #22c55e; }
        .footer-section { background-color: #040812; color: #9ca3af; padding: 40px 0 20px 0; border-top: 1px solid #1f2937; font-size: 14px; }
        .footer-section a { color: #9ca3af; text-decoration: none; }
        .footer-section a:hover { color: #ffffff; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="brand-logo" href="/">TaskPayBD</a>
            <div class="ms-auto d-flex align-items-center">
                {% if 'user' in session %}
                    <a href="/dashboard" class="btn btn-outline-success rounded-pill px-4 me-2">ড্যাশবোর্ড</a>
                    <a href="/logout" class="btn btn-outline-danger rounded-pill px-4">লগ আউট</a>
                {% else %}
                    <a href="/login" class="btn btn-outline-success rounded-pill px-4 me-2">লগ ইন</a>
                    <a href="/signup" class="btn btn-green rounded-pill px-4">রেজিস্ট্রেশন</a>
                {% endif %}
            </div>
        </div>
    </nav>

    <div class="container-fluid px-0">
        {{ content | safe }}
    </div>

    <footer class="footer-section">
        <div class="container">
            <div class="row">
                <div class="col-md-4 mb-4">
                    <h5 class="fw-bold text-white">TaskPayBD</h5>
                    <p class="small text-white">TaskPayBD একটি পেইড সার্ভে প্ল্যাটফর্ম যার মাধ্যমে ঘরে বসে সহজে আয় করা যায়।</p>
                </div>
                <div class="col-md-4 mb-4">
                    <h6 class="fw-bold text-white">দ্রুত লিঙ্ক</h6>
                    <ul class="list-unstyled small">
                        <li><a href="/">হোম</a></li>
                        <li><a href="#">কিভাবে কাজ করে</a></li>
                    </ul>
                </div>
                <div class="col-md-4 mb-4">
                    <h6 class="fw-bold text-white">যোগাযোগ ও সাহায্য</h6>
                    <p class="small mb-1 text-white">Email: arefinhossain345@gmail.com</p>
                    <p class="small text-white">ঠিকানা: ঢাকা, বাংলাদেশ</p>
                </div>
            </div>
            <hr class="border-secondary">
            <div class="text-center small pb-3 text-white">
                &copy; ২০২৬ TaskPayBD. সর্বস্বত্ব সংরক্ষিত।
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function togglePassword(fieldId, iconId) {
            const passwordField = document.getElementById(fieldId);
            const icon = document.getElementById(iconId);
            if (passwordField.type === "password") {
                passwordField.type = "text";
                icon.classList.remove("fa-eye");
                icon.classList.add("fa-eye-slash");
            } else {
                passwordField.type = "password";
                icon.classList.remove("fa-eye-slash");
                icon.classList.add("fa-eye");
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    
    content = '''
        <div class="hero-section">
            <div class="container">
                <h1 class="display-5 fw-bold mb-4 text-white">পেইড সার্ভে করে আয় করুন</h1>
                <div class="row g-4 mt-3">
                    <div class="col-md-4">
                        <div class="feature-card text-start">
                            <h5 class="fw-bold text-success mb-2">⏱️ দ্রুত সার্ভে</h5>
                            <p class="small text-white mb-0">সহজ সার্ভে সম্পন্ন করে দ্রুত পয়েন্ট অর্জন করুন।</p>
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
            </div>
        </div>
    '''
    return render_template_string(BASE_TEMPLATE, content=content)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            error = "পাসওয়ার্ড এবং নিশ্চিতকরণ পাসওয়ার্ড একই হতে হবে!"
        elif len(password) < 6:
            error = "পাসওয়ার্ড অন্তত ৬ অক্ষরের হতে হবে!"
        else:
            try:
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
                if cursor.fetchone():
                    error = "এই ইমেইলটি ইতিমধ্যে রেজিস্টার্ড!"
                else:
                    otp = str(random.randint(100000, 999999))
                    cursor.execute("INSERT OR REPLACE INTO temp_users (email, password, otp) VALUES (?, ?, ?)", (email, password, otp))
                    conn.commit()
                    conn.close()
                    
                    if send_otp_email(email, otp):
                        session['pending_email'] = email
                        return redirect(url_for('verify_otp'))
                    else:
                        error = "ওটিপি ইমেইল পাঠানো যায়নি। অ্যাপ পাসওয়ার্ড বা ইমেইল চেক করুন।"
            except Exception as e:
                error = f"ত্রুটি ঘটেছে: {e}"

    content = f'''
        <div class="container my-5">
            <div class="main-card">
                <h3 class="fw-bold mb-2 text-center text-success">রেজিস্ট্রেশন করুন</h3>
                {f'<div class="alert alert-danger py-2 small">{error}</div>' if error else ''}
                <form method="POST">
                    <div class="mb-3">
                        <input type="email" class="form-control" name="email" required placeholder="ই-মেইল">
                    </div>
                    <div class="mb-3 input-group">
                        <input type="password" class="form-control" name="password" id="regPass" required placeholder="পাসওয়ার্ড">
                        <span class="input-group-text" onclick="togglePassword('regPass', 'regIcon')">
                            <i class="fa-solid fa-eye" id="regIcon"></i>
                        </span>
                    </div>
                    <div class="mb-3 input-group">
                        <input type="password" class="form-control" name="confirm_password" id="confPass" required placeholder="পাসওয়ার্ড নিশ্চিত করুন">
                        <span class="input-group-text" onclick="togglePassword('confPass', 'confIcon')">
                            <i class="fa-solid fa-eye" id="confIcon"></i>
                        </span>
                    </div>
                    <button type="submit" class="btn btn-green w-100 py-2">ওটিপি পাঠান</button>
                </form>
                <p class="text-center mt-3 small text-white">ইতিমধ্যে অ্যাকাউন্ট আছে? <a href="/login" class="text-success fw-bold">লগ ইন করুন</a></p>
            </div>
        </div>
    '''
    return render_template_string(BASE_TEMPLATE, content=content)

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
            password = row[0]
            cursor.execute("INSERT INTO users (email, password, balance) VALUES (?, ?, ?)", (email, password, 0.00))
            cursor.execute("DELETE FROM temp_users WHERE email = ?", (email,))
            conn.commit()
            conn.close()
            
            session.pop('pending_email', None)
            session['user'] = email
            return redirect(url_for('dashboard'))
        else:
            error = "ভুল ওটিপি কোড! আবার চেষ্টা করুন।"
        conn.close()

    content = f'''
        <div class="container my-5">
            <div class="main-card">
                <h3 class="fw-bold mb-2 text-center text-success">ইমেইল ভেরিফিকেশন</h3>
                <p class="text-center small text-white">আপনার ইমেইলে পাঠানো ৬ ডিজিটের ওটিপি কোডটি লিখুন।</p>
                {f'<div class="alert alert-danger py-2 small">{error}</div>' if error else ''}
                <form method="POST">
                    <div class="mb-3">
                        <input type="text" class="form-control text-center" name="otp" required placeholder="______" maxlength="6" style="letter-spacing: 5px; font-size: 20px;">
                    </div>
                    <button type="submit" class="btn btn-green w-100 py-2">ভেরিফাই করুন</button>
                </form>
            </div>
        </div>
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
            error = "ভুল ইমেইল বা পাসওয়ার্ড!"

    content = f'''
        <div class="container my-5">
            <div class="main-card">
                <h3 class="fw-bold mb-3 text-center text-success">লগ ইন করুন</h3>
                {f'<div class="alert alert-danger py-2 small">{error}</div>' if error else ''}
                <form method="POST">
                    <div class="mb-3">
                        <input type="email" class="form-control" name="email" required placeholder="name@example.com">
                    </div>
                    <div class="mb-3 input-group">
                        <input type="password" class="form-control" name="password" id="loginPass" required placeholder="••••••••">
                        <span class="input-group-text" onclick="togglePassword('loginPass', 'loginIcon')">
                            <i class="fa-solid fa-eye" id="loginIcon"></i>
                        </span>
                    </div>
                    <button type="submit" class="btn btn-green w-100 py-2">লগ ইন</button>
                </form>
                <p class="text-center mt-3 small text-white">অ্যাকাউন্ট নেই? <a href="/signup" class="text-success fw-bold">রেজিস্ট্রেশন করুন</a></p>
            </div>
        </div>
    '''
    return render_template_string(BASE_TEMPLATE, content=content)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    user_email = session['user']
    
    message = ""
    error = ""

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
        current_balance = row[0] if row else 0.0

        if amount < 5.0:
            error = "ন্যূনতম উইথড্র পরিমাণ ৫.০০ USD!"
        elif amount > current_balance:
            error = "পর্যাপ্ত ব্যালেন্স নেই!"
        else:
            new_balance = current_balance - amount
            cursor.execute("UPDATE users SET balance = ? WHERE email = ?", (new_balance, user_email))
            cursor.execute("INSERT INTO withdraws (email, method, number, amount, status) VALUES (?, ?, ?, ?, ?)",
                           (user_email, method, number, amount, 'Pending'))
            conn.commit()
            message = "উইথড্র রিকোয়েস্ট সফলভাবে সাবমিট হয়েছে!"
        conn.close()

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE email = ?", (user_email,))
    row = cursor.fetchone()
    cursor.execute("SELECT method, number, amount, status FROM withdraws WHERE email = ? ORDER BY id DESC", (user_email,))
    withdraw_history = cursor.fetchall()
    conn.close()
    
    balance = row[0] if row else 0.00
    
    history_html = ""
    for w in withdraw_history:
        history_html += f'''
            <tr>
                <td>{w[0]}</td>
                <td>{w[1]}</td>
                <td>${w[2]:.2f}</td>
                <td><span class="badge bg-warning text-dark">{w[3]}</span></td>
            </tr>
        '''

    content = f'''
        <div class="container my-5">
            <div class="row">
                <div class="col-md-12 mb-4">
                    <div class="main-card" style="max-width:100%;">
                        <h4 class="text-white">ড্যাশবোর্ড ওভারভিউ</h4>
                        <p class="text-white mb-0">স্বাগতম, <strong>{user_email}</strong></p>
                    </div>
                </div>

                <div class="col-md-4 mb-3">
                    <div class="main-card text-center" style="max-width:100%;">
                        <h6 class="text-white">অ্যাকাউন্ট ব্যালেন্স</h6>
                        <h2 class="fw-bold text-success mb-3">${balance:.2f} USD</h2>
                        <hr class="border-secondary">
                        <h5 class="text-white fw-bold mb-3">টাকা তুলুন (বিকাশ/নগদ)</h5>
                        {f'<div class="alert alert-success py-2 small">{message}</div>' if message else ''}
                        {f'<div class="alert alert-danger py-2 small">{error}</div>' if error else ''}
                        <form method="POST">
                            <div class="mb-3 text-start">
                                <label class="form-label small text-white">পেমেন্ট মেথড</label>
                                <select class="form-select" name="method" required>
                                    <option value="Bkash">বিকাশ (Bkash)</option>
                                    <option value="Nagad">নগদ (Nagad)</option>
                                </select>
                            </div>
                            <div class="mb-3 text-start">
                                <label class="form-label small text-white">একাউন্ট নম্বর</label>
                                <input type="text" class="form-control" name="number" required placeholder="01XXXXXXXXX">
                            </div>
                            <div class="mb-3 text-start">
                                <label class="form-label small text-white">পরিমাণ (USD)</label>
                                <input type="number" step="0.01" class="form-control" name="amount" required placeholder="5.00">
                            </div>
                            <button type="submit" class="btn btn-green w-100 py-2">উইথড্র রিকোয়েস্ট পাঠান</button>
                        </form>
                    </div>
                </div>

                <div class="col-md-8">
                    <div class="main-card mb-4" style="max-width:100%;">
                        <h5 class="fw-bold text-white">অফারওয়াল (CPX Research & BitLabs)</h5>
                        <hr class="border-secondary">
                        <p class="text-white small">নিচের অফারওয়াল থেকে সার্ভে সম্পূর্ণ করে আপনার একাউন্টে ইনস্ট্যান্ট ডলার যোগ করতে পারবেন।</p>
                        <div class="p-4 bg-dark rounded border border-secondary text-center">
                            <h6 class="text-success fw-bold mb-2">CPX Research & BitLabs Survey Wall</h6>
                            <p class="small text-white mb-3">সার্ভে লোড করার জন্য আপনার অফারওয়াল আইফ্রেম এখানে যুক্ত করা হবে।</p>
                            <button class="btn btn-green btn-sm px-4">সার্ভে শুরু করুন</button>
                        </div>
                    </div>

                    <div class="main-card" style="max-width:100%;">
                        <h5 class="fw-bold text-white mb-3">উইথড্র হিস্ট্রি</h5>
                        <div class="table-responsive">
                            <table class="table table-dark table-striped table-bordered small text-center align-middle">
                                <thead>
                                    <tr>
                                        <th>মেথড</th>
                                        <th>নম্বর</th>
                                        <th>পরিমাণ</th>
                                        <th>স্ট্যাটাস</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {history_html if history_html else '<tr><td colspan="4" class="text-muted">কোনো উইথড্র রেকর্ড নেই।</td></tr>'}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    '''
    return render_template_string(BASE_TEMPLATE, content=content)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
