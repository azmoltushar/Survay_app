import os
import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "super_secret_free_survey_key"

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
    <title>TaskPayBD - Paid Survey Kore Ay Korun</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #0b132b; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #ffffff; margin: 0; }
        .navbar { background: #0b132b; border-bottom: 1px solid #1c2541; padding: 15px 30px; }
        .brand-logo { font-weight: 800; font-size: 24px; color: #4ade80; text-decoration: none; }
        .btn-custom-green { background-color: #10b981; color: white; font-weight: 600; border-radius: 6px; padding: 8px 20px; text-decoration: none; }
        .btn-custom-green:hover { background-color: #059669; color: white; }
        .hero-section { background: linear-gradient(180deg, #134e4a 0%, #0b132b 100%); padding: 60px 20px; text-align: center; border-bottom: 2px solid #1c2541; }
        .feature-card { background: #1c2541; border: 1px solid #3a506b; border-radius: 12px; padding: 25px; height: 100%; transition: 0.3s; }
        .feature-card:hover { border-color: #10b981; }
        .step-box { background: #1c2541; border-radius: 10px; padding: 20px; margin-top: 15px; }
        .cta-banner { background: linear-gradient(135deg, #065f46 0%, #047857 100%); border-radius: 12px; padding: 40px; margin: 50px 0; text-align: center; border: 1px solid #10b981; }
        .footer-section { background-color: #070d1b; color: #94a3b8; padding: 40px 0 20px 0; border-top: 1px solid #1c2541; font-size: 14px; }
        .footer-section a { color: #94a3b8; text-decoration: none; }
        .footer-section a:hover { color: #ffffff; }
        .form-card { background: #1c2541; border: 1px solid #3a506b; border-radius: 12px; padding: 30px; max-width: 450px; margin: 40px auto; }
        .form-control { background-color: #0b132b; border: 1px solid #3a506b; color: white; padding: 12px; }
        .form-control:focus { background-color: #0b132b; color: white; border-color: #10b981; box-shadow: none; }
    </style>
</head>
<body>

    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="brand-logo" href="/">TaskPayBD</a>
            <div class="ms-auto d-flex align-items-center">
                <a href="/login" class="btn btn-outline-light rounded-pill px-4 me-2">Log in</a>
                <a href="/signup" class="btn btn-custom-green rounded-pill px-4">Rajistreshon</a>
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
                    <p class="small">TaskPayBD-ekti cholito survey platform ba offerwall-er joriye ghore bose income er sujog deye.</p>
                </div>
                <div class="col-md-4 mb-4">
                    <h6 class="fw-bold text-white">Druto Link</h6>
                    <ul class="list-unstyled small">
                        <li><a href="/">Home</a></li>
                        <li><a href="#">Kibhabe kaj kore</a></li>
                        <li><a href="#">Sahajjo</a></li>
                        <li><a href="#">Amader byaboharkari</a></li>
                    </ul>
                </div>
                <div class="col-md-4 mb-4">
                    <h6 class="fw-bold text-white">Yogayog o shohayota</h6>
                    <p class="small mb-1">Email: support@taskpaybd.com</p>
                    <p class="small mb-1">Telegram: @TaskPayBD_Support</p>
                    <p class="small">Thikana: Dhaka, Bangladesh</p>
                </div>
            </div>
            <hr class="border-secondary">
            <div class="text-center small pb-3">
                &copy; 2026 TaskPayBD. Sarbobhoumo songrokkhito.
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
                <h1 class="display-5 fw-bold mb-4">Paid survey kore ay korun!</h1>
                <div class="row g-4 mt-3">
                    <div class="col-md-4">
                        <div class="feature-card text-start">
                            <h5 class="fw-bold text-success mb-2">⏱️ Druto survey (5-10 minit)</h5>
                            <p class="small text-muted mb-0">Sohor survey somponno kore druto point orjon korun.</p>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="feature-card text-start">
                            <h5 class="fw-bold text-success mb-2">💳 Tatkkonik cashout</h5>
                            <p class="small text-muted mb-0">Bikash ebong nagoder maddhome sahajje apnar taka buje nin.</p>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="feature-card text-start">
                            <h5 class="fw-bold text-success mb-2">👤 100% free rajistreshon</h5>
                            <p class="small text-muted mb-0">Kono khoroch chara aj-i apnar account toiri korun.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="container my-5 text-center">
            <h2 class="fw-bold mb-3">Kibhabe shuru korben?</h2>
            <p class="text-muted mb-5">Matro 3-ti sohoje dhap-e shuru korun.</p>
            <div class="row">
                <div class="col-md-4">
                    <div class="step-box">
                        <span class="badge bg-success rounded-pill px-3 py-2 mb-2">1</span>
                        <h5 class="fw-bold">Free account toiri korun</h5>
                        <p class="small text-muted">Apnar nam ebong email diye matro 1 minit-e free account khulun.</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="step-box">
                        <span class="badge bg-success rounded-pill px-3 py-2 mb-2">2</span>
                        <h5 class="fw-bold">Survey puron korun</h5>
                        <p class="small text-muted">Apnar jonne upojukto surveygulo nirbachon korun ebong sothik uttor din.</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="step-box">
                        <span class="badge bg-success rounded-pill px-3 py-2 mb-2">3</span>
                        <h5 class="fw-bold">Taka tule nin (Bikash/Nagad)</h5>
                        <p class="small text-muted">Sulav porimaner balance orjon korai tikas ba nagod-e withdraw din.</p>
                    </div>
                </div>
            </div>

            <div class="cta-banner">
                <h3 class="fw-bold mb-3">Aj-i shuru korun apnar (paid survey yatra)!</h3>
                <p class="small mb-4">Kono oviggota ba viniyog chara shuru kora jay.</p>
                <a href="/signup" class="btn btn-light text-success fw-bold px-4 py-2 rounded-pill">Ekhoni free account toiri korun</a>
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
            error = "Ei email-ti already registered ache!"

    content = f'''
        <div class="container my-5">
            <div class="form-card">
                <h3 class="fw-bold mb-3 text-center text-success">TaskPayBD Rajistreshon</h3>
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
                    <button type="submit" class="btn btn-custom-green w-100 py-2">Account Khulun</button>
                </form>
                <p class="text-center mt-3 small text-muted">Already account ache? <a href="/login" class="text-success fw-bold">Log in korun</a></p>
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
            error = "Bhul email ba password!"

    content = f'''
        <div class="container my-5">
            <div class="form-card">
                <h3 class="fw-bold mb-3 text-center text-success">Log in korun</h3>
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
                    <button type="submit" class="btn btn-custom-green w-100 py-2">Log in</button>
                </form>
                <p class="text-center mt-3 small text-muted">Account nei? <a href="/signup" class="text-success fw-bold">Rajistreshon korun</a></p>
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
                    <div class="form-card" style="max-width:100%;">
                        <h4>Dashboard Overview</h4>
                        <p class="text-muted mb-0">Swagotom, <strong>{user_email}</strong></p>
                    </div>
                </div>
                <div class="col-md-4 mb-3">
                    <div class="form-card text-center" style="max-width:100%;">
                        <h6 class="text-muted">Account Balance</h6>
                        <h2 class="fw-bold text-success">${balance:.2f} USD</h2>
                    </div>
                </div>
                <div class="col-md-8">
                    <div class="form-card" style="max-width:100%;">
                        <h5 class="fw-bold">Available Surveys & Offerwalls</h5>
                        <hr>
                        <p class="text-muted small">CPX Research ebong BitLabs survey offerwalls ekhane load hobe.</p>
                        <button class="btn btn-custom-green btn-sm" disabled>Survey Load Hoche...</button>
                    </div>
                </div>
            </div>
            <div class="text-center mt-4">
                <a href="/logout" class="btn btn-outline-danger btn-sm">Log out korun</a>
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
