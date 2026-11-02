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
                    <a href="/logout" class="btn btn-outline-danger rounded-pill px
