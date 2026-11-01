import os
import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "taskpaybd_secure_secret_key"

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

init_db()

BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TaskPayBD - Paid Survey Platform</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #070d1b; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .navbar { background: #070d1b; border-bottom: 1px solid #1c2541; padding: 15px 30px; }
        .brand-logo { font-weight: 800; font-size: 24px; color: #22c55e; text-decoration: none; }
        .btn-green { background-color: #16a34a; color: white; font-weight: 600; border-radius: 6px; padding: 8px 20px; text-decoration: none; }
        .btn-green:hover { background-color: #15803d; color: white; }
        .main-card { background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 30px; max-width: 500px; margin: 40px auto; }
        .form-control { background-color: #030712; border: 1px solid #374151; color: white; padding: 12px; }
        .form-control:focus { background-color: #030712; color: white; border-color: #22c55e; box-shadow: none; }
        
        /* Custom styling for cards to make text bright white */
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
                    <p class="small text-white">TaskPayBD-একটি চলিত সার্ভে প্ল্যাটফর্ম বা অফারওয়ালের জরীয়ে ঘরে বসে ইনকামের সুযোগ দেয়।</p>
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
                    <p class="small mb-1"><a href="https://facebook.com" target="_blank">Facebook: Profile Link</a></p>
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
                            <h5 class="fw-bold text-success mb-2">⏱️ দ্রুত সার্ভে (৫-১০ মিনিট)</h5>
                            <p class="small text-white mb-0">সহজ সার্ভে সম্পন্ন করে দ্রুত পয়েন্ট অর্জন করুন।</p>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="feature-card text-start">
                            <h5 class="fw-bold text-success mb-2">💳 তাৎক্ষণিক ক্যাশআউট</h5>
                            <p class="small text-white mb-0">বিকাশ এবং নগদের মাধ্যম সাহায্যে আপনার টাকা তুলে নিন।</p>
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

        <div class="container my-5 text-center">
            <h2 class="fw-bold mb-3 text-white">কিভাবে শুরু করবেন?</h2>
            <p class="text-white mb-5">মাত্র ৩ টি সহজে ধাপে কার্য শুরু করুন।</p>
            <div class="row">
                <div class="col-md-4">
                    <div class="step-box text-start">
                        <span class="badge bg-success rounded-pill px-3 py-2 mb-2">১</span>
                        <h5 class="fw-bold text-white">ফ্রি অ্যাকাউন্ট তৈরি করুন:</h5>
                        <p class="small text-white mb-0">আপনার নাম এবং ইমেইল দিয়ে মাত্র ১ মিনিটেই ফ্রি অ্যাকাউন্ট খুলুন।</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="step-box text-start">
                        <span class="badge bg-success rounded-pill px-3 py-2 mb-2">২</span>
                        <h5 class="fw-bold text-white">সার্ভে পূরণ করুন:</h5>
                        <p class="small text-white mb-0">আপনার জন্য উপযোগী সার্ভেগুলো নির্বাচন করুন এবং সঠিক উত্তর দিন।</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="step-box text-start">
                        <span class="badge bg-success rounded-pill px-3 py-2 mb-2">৩</span>
                        <h5 class="fw-bold text-white">টাকা তুলে নিন (বিকাশ/নগদ):</h5>
                        <p class="small text-white mb-0">সুলভ পরিমাণমাত্র ব্যালেন্স অর্জন করলেই বিকাশ বা নগদ-এ পেমেন্ট দিন।</p>
                    </div>
                </div>
            </div>

            <div class="cta-banner">
                <h3 class="fw-bold mb-3 text-white">আজই শুরু করুন আপনার পেইড সার্ভে যাত্রা!</h3>
                <p class="small text-white mb-4">কোনো অভিজ্ঞতা বা বিনিয়োগ ছাড়াই কাজ শুরু করা যায়।</p>
                <a href="/signup" class="btn btn-light text-success fw-bold px-4 py-2 rounded-pill">এখনই ফ্রি অ্যাকাউন্ট তৈরি করুন</a>
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
        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (email, password, balance) VALUES (?, ?, ?)", (email, password, 0.00))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            error = "এই ইমেইলটি ইতিমধ্যে রেজিস্টার্ড!"

    content = f'''
        <div class="container my-5">
            <div class="main-card">
                <h3 class="fw-bold mb-3 text-center text-success">TaskPayBD রেজিস্ট্রেশন</h3>
                {f'<div class="alert alert-danger py-2 small">{error}</div>' if error else ''}
                <form method="POST">
                    <div class="mb-3">
                        <label class="form-label small">Email address</label>
                        <input type="email" class="form-control" name="email" required placeholder="name@example.com">
                    </div>
                    <div class="mb-3">
                        <label class="form-label small">Password</label>
                        <input type="password" class="form-control" name="password" required placeholder="••••••••">
                    </div>
                    <button type="submit" class="btn btn-green w-100 py-2">অ্যাকাউন্ট খুলুন</button>
                </form>
                <p class="text-center mt-3 small text-muted">ইতিমধ্যে অ্যাকাউন্ট আছে? <a href="/login" class="text-success fw-bold">লগ ইন করুন</a></p>
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
                        <label class="form-label small">Email address</label>
                        <input type="email" class="form-control" name="email" required placeholder="name@example.com">
                    </div>
                    <div class="mb-3">
                        <label class="form-label small">Password</label>
                        <input type="password" class="form-control" name="password" required placeholder="••••••••">
                    </div>
                    <button type="submit" class="btn btn-green w-100 py-2">লগ ইন</button>
                </form>
                <p class="text-center mt-3 small text-muted">অ্যাকাউন্ট নেই? <a href="/signup" class="text-success fw-bold">রেজিস্ট্রেশন করুন</a></p>
            </div>
        </div>
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
        <div class="container my-5">
            <div class="row">
                <div class="col-md-12 mb-4">
                    <div class="main-card" style="max-width:100%;">
                        <h4>ড্যাশবোর্ড ওভারভিউ</h4>
                        <p class="text-muted mb-0">স্বাগতম, <strong>{user_email}</strong></p>
                    </div>
                </div>
                <div class="col-md-4 mb-3">
                    <div class="main-card text-center" style="max-width:100%;">
                        <h6 class="text-muted">অ্যাকাউন্ট ব্যালেন্স</h6>
                        <h2 class="fw-bold text-success">${balance:.2f} USD</h2>
                    </div>
                </div>
                <div class="col-md-8">
                    <div class="main-card" style="max-width:100%;">
                        <h5 class="fw-bold">উপলব্ধ সার্ভে এবং অফারওয়াল</h5>
                        <hr>
                        <p class="text-muted small">সিপিএক্স রিসার্চ এবং বিটল্যাবস সার্ভে অফারওয়াল এখানে লোড হবে।</p>
                        <button class="btn btn-green btn-sm" disabled>সার্ভে লোড হচ্ছে...</button>
                    </div>
                </div>
            </div>
            <div class="text-center mt-4">
                <a href="/logout" class="btn btn-outline-danger btn-sm">লগ আউট করুন</a>
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
