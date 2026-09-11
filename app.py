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
import matplotlib.pyplot as plt
import mplfinance as mpf

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID", "@Smcpaviebotchannel")
EAT = pytz.timezone("Africa/Nairobi")

app = Flask(__name__)

@app.route("/")
def home():
    return "LIVE BOT 24/7 @Smcpaviebotchannel - ALL SESSIONS"

@app.route("/test")
def test():
    send_text("TEST LIVE - @Smcpaviebotchannel connected OK")
    return "Test sent"

def send_text(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=15)
    except Exception as e:
        print(f"Send error: {e}")

def bot_loop():
    print("LIVE BOT 24/7 STARTED")
    send_text("LIVE BOT 24/7 START
