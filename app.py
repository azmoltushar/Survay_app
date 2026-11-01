import os
import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "super_secret_free_survey_key"

# Database initialization
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

# Professional SurveyLama Style Template
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TaskPayBD -Ghore Bose Survey Kore Income</title>
    <!-- Bootstrap 5 CSS CDN -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; }
        .navbar { background: #ffffff; border-bottom: 1px solid #eaeaea; padding: 15px 0; }
        .brand-logo { font-weight: 800; font-size: 24px; color: #2c3e50; text-decoration: none; }
        .btn-custom-red { background-color: #ff6b6b; color: white; font-weight: 600; border-radius: 20px; padding: 8px 25px; }
        .btn-custom-red:hover { background-color: #fa5252; color: white; }
        .hero-title { font-size: 38px; font-weight: 800; color: #2b3a4a; line-height: 1.3; }
        .hero-desc { font-size: 16px; color: #555; margin-top: 15px; line-height: 1.6; }
        .login-card { background: #ffffff; border: 1px solid #e5e5e5; border-radius: 12px; padding: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); }
        .form-control { border-radius: 20px; padding: 12px 20px; background-color: #f8f9fa; border: 1px solid #ced4da; }
        .footer-section { background-color: #4db6ac; color: white; padding: 40px 0 20px 0; margin-top: 80px; }
        .footer-section a { color: white; text-decoration: none; }
        .footer-section a:hover { text-decoration: underline; }
    </style>
</head>
<body>

    <!-- Header / Navbar -->
    <nav class="navbar navbar-expand-lg navbar-light sticky-top">
        <div class="container">
            <a class="brand-logo" href="/">TaskPayBD</a>
            <div class="ms-auto d-flex align-items-center">
                <a href="/" class="text-dark text-decoration-name me-4 fw-semibold d-none d-md-inline">Swagotom</a>
                <a href="/" class="text-dark text-decoration-name me-4 fw-semibold d-none d-md-inline">Kibhabe kaj kore</a>
                <a href="/signup" class="btn btn-custom-red me-2">Nibondhon</a>
                <a href="/login" class="btn btn-outline-dark rounded-pill px-4">Log in</a>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="container my-5">
        {{ content | safe }}
    </div>

    <!-- Footer -->
    <footer class="footer-section">
        <div class="container">
            <div class="row">
                <div class="col-md-4 mb-4">
                    <h5 class="fw-bold">TASKPAYBD</h5>
                    <p class="small">Online survey. Ponnokh o poriseba unnoto korte survey-te anshon nin ebong apnar motamot shear korun.</p>
                </div>
                <div class="col-md-4 mb-4">
                    <h6 class="fw-bold">Amader Somporke</h6>
                    <ul class="list-unstyled small">
                        <li><a href="#">Kibhabe eta kaj kore</a></li>
                        <li><a href="#">Sahajjo</a></li>
                        <li><a href="#">Prashnoi jiggeshito proshnaboli</a></li>
                    </ul>
                </div>
                <div class="col-md-4 mb-4">
                    <h6 class="fw-bold">Site-er Bhasha</h6>
                    <select class="form-select form-select-sm w-50 bg-light text-dark">
                        <option selected>Bangla - BENGALI</option>
                    </select>
                </div>
            </div>
            <hr class="border-light">
            <div class="text-center small pb-3">
                <a href="#" class="me-3">Sodosshopod sortaboli</a> | 
                <a href="#" class="mx-3">Aini notish</a> | 
                <a href="#" class="mx-3">Goponiyota niti</a> | 
                <a href="#" class="mx-3">Purashkar system</a>
            </div>
        </div>
    </footer>

    <!-- Bootstrap 5 JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    
    content = '''
        <div class="row align-items-center">
            <!-- Left Side Text Banner -->
            <div class="col-lg-7 mb-5 mb-lg-0 pe-lg-5">
                <h1 class="hero-title">Ghore bose proti survey-te 600 tk porjonto ay korun!</h1>
                <p class="hero-desc">Paid online survey-te anshon korun ebong proti mase 20000 tk porjonto ay korun!</p>
                <div class="mt-4">
                    <h5 class="fw-bold text-dark">Kibhabe?</h5>
                    <p class="text-muted small">Protiti somponno survey-er jonno, apni payment paben ja apni nagode rupantor korte parben.</p>
                </div>
                <div class="mt-3">
                    <h5 class="fw-bold text-dark">Aro o beshi taka ay korte chan?</h5>
                    <p class="text-muted small">Bonus pete dine 3-ti survey-er uttor din! Proti mase chomok, challenge, protijogita ebong aro onek kichu bhule na giye.</p>
                </div>
            </div>

            <!-- Right Side Login Box (SurveyLama Style) -->
            <div class="col-lg-5">
                <div class="login-card">
                    <h3 class="fw-bold mb-2">Ekhoni log in korun</h3>
                    <p class="text-muted small mb-4">Ami aro purushkar pete log in kori.</p>
                    <form method="POST" action="/login">
                        <div class="mb-3">
                            <input type="email" class="form-control" name="email" required placeholder="Apnar email din">
                        </div>
                        <div class="mb-3">
                            <input type="password" class="form-control" name="password" required placeholder="Password din">
                        </div>
                        <div class="mb-3 text-end">
                            <a href="#" class="small text-decoration-none text-muted">Apnar password bhule gechen?</a>
                        </div>
                        <button type="submit" class="btn btn-custom-red w-100 py-2">Log in korun</button>
                    </form>
                    <p class="text-center mt-3 small text-muted">Account nei? <a href="/signup" class="fw-bold text-danger">Nibondhon korun</a></p>
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
        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (email, password, balance) VALUES (?, ?, ?)", (email, password, 0.00))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            error = "Ei email-ti already registered!"

    content = f'''
        <div class="row justify-content-center">
            <div class="col-md-5">
                <div class="login-card">
                    <h3 class="fw-bold mb-3 text-center">TaskPayBD Nibondhon</h3>
                    {f'<div class="alert alert-danger py-2 small">{error}</div>' if error else ''}
                    <form method="POST">
                        <div class="mb-3">
                            <input type="email" class="form-control" name="email" required placeholder="Email address">
                        </div>
                        <div class="mb-3">
                            <input type="password" class="form-control" name="password" required placeholder="Password">
                        </div>
                        <button type="submit" class="btn btn-custom-red w-100 py-2">Account Khulun</button>
                    </form>
                    <p class="text-center mt-3 small">Already account ache? <a href="/login" class="text-danger">Log in korun</a></p>
                </div>
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
        <div class="row justify-content-center">
            <div class="col-md-5">
                <div class="login-card">
                    <h3 class="fw-bold mb-3 text-center">Log in</h3>
                    {f'<div class="alert alert-danger py-2 small">{error}</div>' if error else ''}
                    <form method="POST">
                        <div class="mb-3">
                            <input type="email" class="form-control" name="email" required placeholder="Email address">
                        </div>
                        <div class="mb-3">
                            <input type="password" class="form-control" name="password" required placeholder="Password">
                        </div>
                        <button type="submit" class="btn btn-custom-red w-100 py-2">Log in korun</button>
                    </form>
                    <p class="text-center mt-3 small">Account nei? <a href="/signup" class="text-danger">Nibondhon korun</a></p>
                </div>
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
        <div class="row">
            <div class="col-md-12 mb-4">
                <div class="login-card bg-light">
                    <h4>Dashboard</h4>
                    <p class="text-muted mb-0">Swagotom, <strong>{user_email}</strong></p>
                </div>
            </div>
            <div class="col-md-4 mb-3">
                <div class="login-card text-center bg-white border-primary">
                    <h6 class="text-muted">Total Balance</h6>
                    <h2 class="fw-bold text-success">${balance:.2f} USD</h2>
                </div>
            </div>
            <div class="col-md-8">
                <div class="login-card">
                    <h5 class="fw-bold">Available Surveys (Offerwall)</h5>
                    <hr>
                    <p class="text-muted small">Ekhane CPX Research ebong BitLabs-er survey offerwalls load hobe.</p>
                    <button class="btn btn-custom-red btn-sm" disabled>Survey Load Hoche...</button>
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
