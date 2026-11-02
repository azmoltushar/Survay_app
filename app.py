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
    <link href="
