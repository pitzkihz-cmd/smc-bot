import os, time, threading, requests, pytz
from flask import Flask
from datetime import datetime
import yfinance as yf
import pandas as pd

BOT_TOKEN = os.getenv("BOT_TOKEN","")
CHAT_ID = os.getenv("CHAT_ID","")
CHANNEL_ID = os.getenv("CHANNEL_ID","")

app = Flask(__name__)

@app.route('/')
def home(): return "GOLD BOT LIVE - OK"

@app.route('/test')
def test():
    send_telegram("✅ TEST OK - Bot Live")
    return "Test sent"

def send_telegram(text):
    try:
        for cid in [CHAT_ID, CHANNEL_ID]:
            if cid and BOT_TOKEN:
                requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id":cid,"text":text,"parse_mode":"Markdown"}, timeout=10)
    except: pass

def bot_loop():
    print("Loop waiting...")
    time.sleep(5)
    # ... your previous logic here - paste my last all-in-one loop
    while True:
        try:
            time.sleep(60)
            # bot will run here
        except Exception as e:
            print(e); time.sleep(30)

threading.Thread(target=bot_loop, daemon=True).start()
