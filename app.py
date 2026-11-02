import os
import sqlite3
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, redirect, url_for, session

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

@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/surveys')
def surveys():
    return render_template('surveys.html') if os.path.exists('templates/surveys.html') else render_template('index.html')

@app.route('/terms')
def terms():
    return render_template('terms.html') if os.path.exists('templates/terms.html') else render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html') if os.path.exists('templates/about.html') else render_template('index.html')

@app.route('/contact')
def contact():
    return render_template('contact.html') if os.path.exists('templates/contact.html') else render_template('index.html')

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
    return render_template('signup.html', error=error)

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

    return render_template('verify_otp.html', error=error) if os.path.exists('templates/verify_otp.html') else render_template('signup.html', error=error)

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
    return render_template('login.html', error=error) if os.path.exists('templates/login.html') else render_template('signup.html', error=error)

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
            cursor.execute("INSERT INTO withdraws (email, method, number, amount, status) VALUES (?, ?, ?, ?, 'Pending')",
                           (user_email, method, number, amount_bdt))
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

    return render_template('dashboard.html', user_email=user_email, balance_bdt=balance_bdt, withdraw_history=withdraw_history, message=message, error=error)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)