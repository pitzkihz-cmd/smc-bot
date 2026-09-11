import os
import time
import requests
import yfinance as yf
import pytz
from flask import Flask
from threading import Thread
from datetime import datetime
import matplotlib
matplotlib.use('Agg')

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID", "https://t.me/Smcpaviebotchannel")
EAT = pytz.timezone("Africa/Nairobi")

app = Flask(__name__)

@app.route("/")
def home():
    return "LIVE BOT RUNNING 24/7 @Smcpaviebotchannel"

@app.route("/test")
def test():
    send_text("TEST LIVE - Bot connected to @Smcpaviebotchannel OK")
    return "Test sent to channel"

def send_text(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=15)
    except Exception as e:
        print(f"Send error: {e}")

def bot_loop():
    print("LIVE BOT 24/7 STARTED")
    send_text("LIVE BOT 24/7 STARTED - @Smcpaviebotchannel - SMC 70-79pct")
    while True:
        try:
            data = yf.download("GC=F", period="1d", interval="5m", progress=False)
            if data is not None and not data.empty:
                price = float(data["Close"].iloc[-1])
                print(f"{datetime.now(EAT)} GOLD {price}")
            time.sleep(60)
        except Exception as e:
            print(f"Loop error: {e}")
            time.sleep(60)

Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
