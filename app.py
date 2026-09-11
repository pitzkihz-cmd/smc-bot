import os, time, requests, json
from flask import Flask
from threading import Thread
import yfinance as yf
from datetime import datetime

# --- CONFIG - YOUR CHANNEL ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID", "@Smcpaviebotchannel") # your channel https://t.me/Smcpaviebotchannel

app = Flask(__name__)

@app.route("/")
def home():
    return "LIVE BOT RUNNING 24/7 - @Smcpaviebotchannel"

@app.route("/test")
def test():
    send_text("🧪 TEST LIVE - Bot connected to @Smcpaviebotchannel ✅\nGold/BTC/EURUSD live feed working\nNext signal auto AFTER hit only")
    return "Test sent to @Smcpaviebotchannel - check your channel"

def send_text(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except Exception as e:
        print(f"Send error: {e}")

def get_price(symbol="GC=F"):
    try:
        # XAUUSD = Gold
        ticker = yf.Ticker(symbol)
        price = ticker.fast_info['last_price']
        return float(price)
    except:
        return None

def bot_loop():
    print("
