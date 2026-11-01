import os
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "super_secret_free_survey_key"

# সাময়িক ডাটাবেজ
users_db = {}

@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return '''
        <h2>Welcome to Global Survey Platform</h2>
        <a href="/signup">Sign Up</a> | <a href="/login">Login</a>
    '''

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users_db:
            return "Email already exists! <a href='/signup'>Try again</a>"
        users_db[email] = {'password': password, 'balance': 0.00}
        return "Registration Successful! <a href='/login'>Click here to Login</a>"
    return '''
        <h3>Sign Up</h3>
        <form method="POST">
            Email: <input type="email" name="email" required><br><br>
            Password: <input type="password" name="password" required><br><br>
            <button type="submit">Register</button>
        </form>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_db.get(email)
        if user and user['password'] == password:
            session['user'] = email
            return redirect(url_for('dashboard'))
        else:
            return "Invalid Credentials! <a href='/login'>Try again</a>"
    return '''
        <h3>Login</h3>
        <form method="POST">
            Email: <input type="email" name="email" required><br><br>
            Password: <input type="password" name="password" required><br><br>
            <button type="submit">Login</button>
        </form>
    '''

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    user_email = session['user']
    user_data = users_db.get(user_email)
    return f'''
        <h2>User Dashboard</h2>
        <p><strong>User:</strong> {user_email}</p>
        <p><strong>Balance:</strong> ${user_data['balance']:.2f} USD</p>
        <hr>
        <h3>Available Surveys</h3>
        <p><em>Offerwall survey network will load here.</em></p>
        <hr>
        <a href="/logout">Logout</a>
    '''

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)