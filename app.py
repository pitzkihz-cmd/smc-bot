from flask import Flask
import threading, time, requests, pytz
from datetime import datetime
import yfinance as yf
import pandas as pd

BOT_TOKEN = "8967884674:AAEYIsjVIkMVZCdUU0P29EKvHMpY2guGKJs"
CHAT_ID = "7804217051"
CHANNEL_ID = "7804217051"

app = Flask(__name__)

@app.route('/')
def home():
    return "GOLD BOT LIVE - @Smcpaviebot - OK"

@app.route('/test')
def test():
    msg = "✅ TEST OK - @Smcpaviebot LIVE\nTime: " + datetime.now(pytz.timezone("Africa/Nairobi")).strftime("%H:%M EAT")
    res = send_telegram(msg)
    return f"RESULT: {res}<br>Check Telegram now"

def send_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
        r = requests.post(url, json=data, timeout=10)
        print(f"Telegram: {r.text}")
        return r.text
    except Exception as e:
        print(f"Error {e}")
        return str(e)

def bot_loop():
    time.sleep(5)
    send_telegram("🚀 GOLD BOT ONLINE - Full Package Active")
    while True:
        try:
            tz = pytz.timezone("Africa/Nairobi")
            now = datetime.now(tz)
            print(f"Scanning {now.strftime('%H:%M')}")
            time.sleep(60)
        except Exception as e:
            print(f"Loop error {e}")
            time.sleep(30)

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
