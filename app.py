from flask import Flask, render_template, request, jsonify, redirect
import json
import time
import base64

app = Flask(__name__)

# In-memory user database (resets on restart)
users = {}

# === M-PESA SANDBOX CREDENTIALS (REPLACE LATER) ===
CONSUMER_KEY = "YOUR_CONSUMER_KEY"
CONSUMER_SECRET = "YOUR_CONSUMER_SECRET"
SHORTCODE = "174379"
PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
CALLBACK_URL = "https://your-ngrok-url.ngrok.io/callback"

import requests

def get_access_token():
    if CONSUMER_KEY == "YOUR_CONSUMER_KEY":
        return "TEST_TOKEN"
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    auth = (CONSUMER_KEY, CONSUMER_SECRET)
    response = requests.get(url, auth=auth)
    return response.json().get('access_token', '')

def stk_push(phone, amount):
    if CONSUMER_KEY == "YOUR_CONSUMER_KEY":
        print(f"TEST MODE: Sending KSh {amount} to {phone}")
        return {"success": True, "message": "Test payout sent!"}
    
    token = get_access_token()
    timestamp = time.strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(f"{SHORTCODE}{PASSKEY}{timestamp}".encode()).decode()
    
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": "QuantumBreath",
        "TransactionDesc": "Earned KSh 5 for breathing"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

@app.route('/')
def home():
    phone = request.args.get('phone')
    if not phone:
        phone = "0712345678"  # Default test
    if phone not in users:
        users[phone] = {"sessions": 0, "earnings": 0}
    return render_template('index.html', user=users[phone], phone=phone)

@app.route('/breathe')
def breathe():
    phone = request.args.get('phone')
    return render_template('breathe.html', phone=phone)

@app.route('/earn', methods=['POST'])
def earn():
    phone = request.json.get('phone')
    if phone and phone in users:
        users[phone]["sessions"] += 1
        users[phone]["earnings"] += 5
        payout = stk_push(phone, 5)
    else:
        payout = {"error": "Invalid phone"}
    return jsonify({"earnings": users[phone]["earnings"], "payout": payout})

@app.route('/tiktok')
def tiktok():
    return redirect("https://tiktok.com/@bullbolt1")

@app.route('/callback', methods=['POST'])
def callback():
    data = request.json
    print("M-PESA CALLBACK:", data)
    return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
