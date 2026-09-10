import os, time, threading, requests, pytz
from flask import Flask
from datetime import datetime
import yfinance as yf
import pandas as pd

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CHANNEL_ID = os.getenv("CHANNEL_ID")

app = Flask(__name__)

@app.route('/')
def home():
    return "GOLD BOT LIVE - Unlimited + Win/Loss Tracker"

@app.route('/test')
def test():
    send_telegram("✅ TEST OK\nYour Gold Bot is LIVE\n• Unlimited entries\n• BE alerts\n• WIN/LOSS tracker\nWaiting for real setup...")
    return "✅ Test sent to Telegram - check your chat"

def send_telegram(text):
    try:
        for cid in [CHAT_ID, CHANNEL_ID]:
            if cid:
                requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": cid, "text": text, "parse_mode":"Markdown"}, timeout=10)
    except Exception as e:
        print(e)

def get_price():
    df = yf.download("GC=F", period="1d", interval="1m", progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    return float(df['Close'].iloc[-1])

def bot_loop():
    active = None
    last_sent = {}
    wins = 0; losses = 0
    print("BOT STARTED - Unlimited")
    time.sleep(10)
    send_telegram("🚀 *GOLD BOT ONLINE*\nUnlimited + BE + Win/Loss\nScanning every 20s\nNY session starts 15:30 EAT")
    
    while True:
        try:
            tz = pytz.timezone("Africa/Nairobi")
            now = datetime.now(tz)
            h = now.hour + now.minute/60

            if active:
                price = get_price()
                side = active['side']
                if not active.get('be_done'):
                    hit_tp1 = (price <= active['tp1'] if side=="SELL" else price >= active['tp1'])
                    if hit_tp1:
                        send_telegram(f"🔔 *BE ALERT*\n{side} TP1 {active['tp1']:.1f} hit! Price {price:.1f}\n👉 Move SL to BE NOW!")
                        active['be_done']=True
                hit_tp = (price <= active['tp3'] if side=="SELL" else price >= active['tp3'])
                hit_sl = (price >= active['sl'] if side=="SELL" else price <= active['sl'])
                if hit_tp:
                    wins+=1
                    send_telegram(f"✅ *WIN +{abs(active['tp3']-active['e2']):.1f}$*\n{side} {active['strat']}\nScore {wins}W-{losses}L")
                    active=None
                elif hit_sl:
                    losses+=1
                    send_telegram(f"❌ *LOSS -{abs(active['sl']-active['e2']):.1f}$*\n{side} {active['strat']}\nScore {wins}W-{losses}L")
                    active=None
                time.sleep(15); continue

            if not (10 <= h <= 23.5): time.sleep(60); continue

            df15 = yf.download("GC=F", period="5d", interval="15m", progress=False, auto_adjust=True)
            df5 = yf.download("GC=F", period="5d", interval="5m", progress=False, auto_adjust=True)
            if isinstance(df15.columns, pd.MultiIndex): df15.columns = df15.columns.get_level_values(0)
            if
