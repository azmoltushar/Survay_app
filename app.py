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
        msg['Subject'] = "TaskPayBD - Email Verification OTP"
        body = f"Apanar TaskPayBD account registration-er jonno OTP code holo: {otp_code}"
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
        .step-box { background: #111827; border: 1px solid #1f2937; border-radius: 10px; padding: 20px; height: 100%; color: #ffffff; }
        .hero-section { background: linear-gradient(180deg, #14532d 0%, #070d1b 100%); padding: 60px 20px; text-align: center; border-bottom: 2px solid #1c2541; }
        .cta-banner { background: linear-gradient(135deg, #14532d 0%, #166534 100%); border-radius: 12px; padding: 40px; margin: 40px 0; text-align: center; border: 1px solid #22c55e; }
        .footer-section { background-color: #040812; color: #9ca3af; padding: 40px 0 20px 0; border-top: 1px solid #1f2937; font-size: 14px; }
        .footer-section a { color: #9ca3af; text-decoration: none; }
        .footer-section a:hover { color: #ffffff; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="brand-logo" href="/">TaskPayBD</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto align-items-center">
                    <li class="nav-item"><a class="nav-link text-white" href="/">হোম</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/surveys">Surveys</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/terms">Terms & Conditions</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/about">About Us</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/contact">Contact Us</a></li>
                </ul>
                <div class="ms-lg-3 d-flex align-items-center mt-3 mt-lg-0">
                    {% if 'user' in session %}
                        <a href="/dashboard" class="btn btn-outline-success rounded-pill px-4 me-2">ড্যাশবোর্ড</a>
                        <a href="/logout" class="btn btn-outline-danger rounded-pill px-4">লগ আউট</a>
                    {% else %}
                        <a href="/login" class="btn btn-outline-success rounded-pill px-4 me-2">লগ ইন</a>
                        <a href="/signup" class="btn btn-green rounded-pill px-4">রেজিস্ট্রেশন</a>
                    {% endif %}
                </div>
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
                    <p class="small text-white">TaskPayBD - Bangladeshi trusted paid survey platform.</p>
                </div>
                <div class="col-md-4 mb-4">
                    <h6 class="fw-bold text-white">দ্রুত লিঙ্ক</h6>
                    <ul class="list-unstyled small">
                        <li><a href="/surveys">Surveys</a></li>
                        <li><a href="/terms">Terms & Conditions</a></li>
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
                &copy; 2026 TaskPayBD. All rights reserved.
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
                <h1 class="display-5 fw-bold mb-3 text-white">পেইড সার্ভে করে আয় করুন</h1>
                <p class="text-light mb-4">TaskPayBD প্ল্যাটফর্মে আপনাকে স্বাগতম। অনলাইন সার্ভে করে প্রতিদিন সহজে ইনকাম করুন।</p>
                <div class="row g-4 mt-2 justify-content-center">
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
            </div>
        </div>

        <div class="container my-5 text-center" style="max-width: 1000px;">
            <h2 class="fw-bold mb-2 text-white">কিভাবে কাজ শুরু করবেন?</h2>
            <p class="text-muted mb-4">মাত্র ৩টি সহজ ধাপে আপনার ইনকাম যাত্রা শুরু করুন:</p>
            <div class="row text-start g-4">
                <div class="col-md-4">
                    <div class="step-box">
                        <h5 class="text-success fw-bold mb-2">১. ফ্রি রেজিস্ট্রেশন</h5>
                        <p class="small text-white mb-0">ইমেইল ও পাসওয়ার্ড দিয়ে খুব সহজেই আপনার ফ্রি একাউন্ট তৈরি করে নিন।</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="step-box">
                        <h5 class="text-success fw-bold mb-2">২. সার্ভে সম্পন্ন করুন</h5>
                        <p class="small text-white mb-0">উপলব্ধ সার্ভেগুলো পূরণ করে আপনার ব্যালেন্স বৃদ্ধি করুন।</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="step-box">
                        <h5 class="text-success fw-bold mb-2">৩. পেমেন্ট গ্রহণ</h5>
                        <p class="small text-white mb-0">মিনিমাম ১০০ টাকা হলেই বিকাশ বা নগদে টাকা তুলে নিন।</p>
                    </div>
                </div>
            </div>

            <div class="cta-banner">
                <h3 class="fw-bold mb-2 text-white">আজই শুরু করুন আপনার পেইড সার্ভে যাত্রা!</h3>
                <p class="small text-light mb-3">কোনো অভিজ্ঞতা বা বিনিয়োগ ছাড়াই কাজ শুরু করা যায়।</p>
                <a href="/signup" class="btn btn-light text-success fw-bold px-4 py-2 rounded-pill">এখনই ফ্রি অ্যাকাউন্ট তৈরি করুন</a>
            </div>
        </div>
    '''
    return render_template_string(BASE_TEMPLATE, content=content)

@app.route('/surveys')
def surveys():
    content = '''
        <div class="container my-5" style="max-width: 800px;">
            <div class="main-card" style="max-width: 100%;">
                <h3 class="fw-bold text-success mb-3">All Available Surveys (সকল উপলব্ধ সার্ভে)</h3>
                <p class="text-white small mb-4">নিচের তালিকা থেকে যেকোনো সার্ভেতে ক্লিক করে কাজ শুরু করতে পারেন:</p>
                <div class="list-group">
                    <div class="list-group-item bg-dark text-white border-secondary mb-3 p-3 rounded">
                        <h5 class="text-success fw-bold">Best Survey #1: CPX Daily Consumer Survey</h5>
                        <p class="small mb-2">Reward: ৳120 BDT (Estimated time: 10 mins)</p>
                        <button class="btn btn-green btn-sm" onclick="alert('Survey starting...')">সার্ভে শুরু করুন</button>
                    </div>
                    <div class="list-group-item bg-dark text-white border-secondary mb-3 p-3 rounded">
                        <h5 class="text-success fw-bold">BitLabs High Paying Opinion Poll</h5>
                        <p class="small mb-2">Reward: ৳250 BDT (Estimated time: 15 mins)</p>
                        <button class="btn btn-green btn-sm" onclick="alert('Survey starting...')">সার্ভে শুরু করুন</button>
                    </div>
                </div>
            </div>
        </div>
    '''
    return render_template_string(BASE_TEMPLATE, content=content)

@app.route('/terms')
def terms():
    content = '''
        <div class="container my-5" style="max-width: 800px;">
            <div class="main-card" style="max-width: 100%;">
                <h3 class="fw-bold text-success mb-3">Terms & Conditions</h3>
                <p class="text-white small">১. প্রতি অ্যাকাউন্টে সঠিক তথ্য দিয়ে কাজ করতে হবে।<br>২. ভুয়া তথ্য দিলে অ্যাকাউন্ট ব্যান হতে পারে।<br>৩. ন্যূনতম উইথড্র ১০০ টাকা।</p>
            </div>
        </div>
    '''
    return render_template_string(BASE_TEMPLATE, content=content)

@app.route('/about')
def about():
    content = '''
        <div class="container my-5" style="max-width: 800px;">
            <div class="main-card" style="max-width: 100%;">
                <h3 class="fw-bold text-success mb-3">About Us</h3>
                <p class="text-white small">TaskPayBD হলো বাংলাদেশের একটি বিশ্বস্ত পেইড সার্ভে প্ল্যাটফর্ম, যার মাধ্যমে ঘরে বসে সহজে আয় করা সম্ভব।</p>
            </div>
        </div>
    '''
    return render_template_string(BASE_TEMPLATE, content=content)

@app.route('/contact')
def contact():
    content = '''
        <div class="container my-5" style="max-width: 800px;">
            <div class="main-card" style="max-width: 100%;">
                <h3 class="fw-bold text-success mb-3">Contact Us</h3>
                <p class="text-white small">যেকোনো প্রয়োজনে আমাদের ইমেইল করুন: arefinhossain345@gmail.com</p>
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
            error = "Password and confirm password must match!"
        else:
            try:
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
                if cursor.fetchone():
                    error = "Email already registered!"
                else:
                    otp = str(random.randint(100000, 999999))
                    cursor.execute("INSERT OR REPLACE INTO temp_users (email, password, otp) VALUES (?, ?, ?)", (email, password, otp))
                    conn.commit()
                    conn.close()
                    if send_otp_email(email, otp):
                        session['pending_email'] = email
                        return redirect(url_for('verify_otp'))
                    else:
                        error = "Failed to send OTP email."
            except Exception as e:
                error = f"Error: {e}"

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
                    <div class="mb-3 form-check text-start">
                        <input type="checkbox" class="form-check-input" id="terms" required>
                        <label class="form-check-label small text-white" for="terms">
                            আমি <a href="/terms" target="_blank" class="text-success">Terms & Conditions</a> পড়েছি এবং সম্মত আছি।
                        </label>
                    </div>
                    <button type="submit" class="btn btn-green w-100 py-2">ওটিপি পাঠান</button>
                </form>
                <p class="text-center mt-3 small text-white">Already have an account? <a href="/login" class="text-success fw-bold">লগ ইন করুন</a></p>
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
            error = "Invalid OTP code!"
        conn.close()

    content = f'''
        <div class="container my-5">
            <div class="main-card">
                <h3 class="fw-bold mb-2 text-center text-success">ইমেইল ভেরিফিকেশন</h3>
                <p class="text-center small text-white">Enter the 6-digit OTP sent to your email.</p>
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
            error = "Invalid email or password!"

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
                <p class="text-center mt-3 small text-white">Don't have an account? <a href="/signup" class="text-success fw-bold">রেজিস্ট্রেশন করুন</a></p>
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
            amount_bdt = float(request.form['amount'])
        except:
            amount_bdt = 0.0

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE email = ?", (user_email,))
        row = cursor.fetchone()
        current_balance_bdt = row[0] if row else 0.0

        if amount_bdt < 100.0:
            error = "ন্যূনতম উইথড্র পরিমাণ ১০০.০০ BDT!"
        elif amount_bdt > current_balance_bdt:
            error = "পর্যাপ্ত ব্যালেন্স নেই!"
        else:
            new_balance = current_balance_bdt - amount_bdt
            cursor.execute("UPDATE users SET balance = ? WHERE email = ?", (new_balance, user_email))
            cursor.execute("INSERT INTO withdraws (email, method, number, amount, status) VALUES (?, ?, ?, ?, ?)",
                           (user_email, method, number, amount_bdt, 'Pending'))
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
    
    balance_bdt = row[0] if row else 0.00
    
    history_html = ""
    for w in withdraw_history:
        history_html += f'''
            <tr>
                <td>{w[0]}</td>
                <td>{w[1]}</td>
                <td>৳{w[2]:.2f}</td>
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
                        <h2 class="fw-bold text-success mb-3">৳{balance_bdt:.2f} BDT</h2>
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
                                <label class="form-label small text-white">পরিমাণ (BDT)</label>
                                <input type="number" step="1.00" class="form-control" name="amount" required placeholder="100">
                            </div>
                            <button type="submit" class="btn btn-green w-100 py-2">উইথড্র রিকোয়েস্ট পাঠান</button>
                        </form>
                    </div>
                </div>

                <div class="col-md-8">
                    <div class="main-card mb-4" style="max-width:100%;">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h5 class="fw-bold text-white mb-0">উপলব্ধ সার্ভে (Available Surveys)</h5>
                            <a href="/surveys" class="btn btn-outline-success btn-sm">সব সার্ভে দেখুন (All Surveys)</a>
                        </div>
                        <hr class="border-secondary">
                        <div class="p-3 bg-dark rounded border border-success mb-3 text-start">
                            <span class="badge bg-success mb-1">Top Best Survey</span>
                            <h6 class="text-white fw-bold">CPX Research Special Survey</h6>
                            <p class="small text-muted mb-2">Reward: ৳150 BDT | Time: 8 mins</p>
                            <a href="/surveys" class="btn btn-green btn-sm px-4">সার্ভে শুরু করুন</a>
                        </div>
                        <div class="p-4 bg-dark rounded border border-secondary text-center">
                            <h6 class="text-success fw-bold mb-2">CPX Research & BitLabs Survey Wall</h6>
                            <p class="small text-white mb-3">এখানে অফারওয়ালের সার্ভে লোড হবে।</p>
                            <a href="/surveys" class="btn btn-green btn-sm px-4">অফারওয়াল সার্ভে দেখুন</a>
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
    app.run(host='0.0.0.0', port=port, debug=True)
