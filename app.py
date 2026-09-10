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
    return "GOLD BOT LIVE - @Smcpaviebot"

@app.route('/test')
def test():
    ok = send_telegram("✅ *TEST OK - @Smcpaviebot is LIVE!*\nGold Bot Full Package Working\nTime: " + datetime.now(pytz.timezone("Africa/Nairobi")).strftime("%H:%M EAT"))
    return f"TELEGRAM SEND = {ok}<br>CHAT_ID={CHAT_ID}<br>Check Telegram NOW @Smcpaviebot"

def send_telegram(text):
    try:
        r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=15)
        print(f"TELEGRAM: {r.status_code} {r.text}")
        return r.text
    except Exception as e:
        print(f"Error: {e}")
        return str(e)

def get_price():
    df = yf.download("GC=F", period="1d", interval="1m", progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    return float(df['Close'].iloc[-1])

def bot_loop():
    active=None; last_sent={}; wins=0; losses=0
    time.sleep(10)
    send_telegram("🚀 *GOLD BOT ONLINE - FULL PACKAGE*\n@Smcpaviebot\nUnlimited + BE + Win/Loss tracking\nScanning NY Session...")
    while True:
        try:
            tz=pytz.timezone("Africa/Nairobi")
            now=datetime.now(tz)
            h=now.hour + now.minute/60

            if active:
                price=get_price()
                side=active['side']
                if not active.get('be_done') and ((price<=active['tp1'] if side=="SELL" else price>=active['tp1'])):
                    send_telegram(f"🔔 *BE ALERT*\n{side} TP1 {active['tp1']:.1f} hit! Move SL to BE!")
                    active['be_done']=True
                if (price<=active['tp3'] if side=="SELL" else price>=active['tp3']):
                    wins+=1
                    send_telegram(f"✅ *WIN +{abs(active['tp3']-active['e2']):.1f}$*\nScore {wins}W-{losses}L")
                    active=None
                elif (price>=active['sl'] if side=="SELL" else price<=active['sl']):
                    losses+=1
                    send_telegram(f"❌ *LOSS - SL hit*\nScore {wins}W-{losses}L")
                    active=None
                time.sleep(15)
                continue

            if not (10 <= h <= 23.5):
                time.sleep(60)
                continue

            df15=yf.download("GC=F", period="5d", interval="15m", progress=False, auto_adjust=True)
            df5=yf.download("GC=F", period="5d", interval="5m", progress=False, auto_adjust=True)
            if isinstance(df15.columns, pd.MultiIndex): df15.columns=df15.columns.get_level_values(0)
            if isinstance(df5.columns, pd.MultiIndex): df5.columns=df5.columns.get_level_values(0)
            df15=df15.dropna(); df5=df5.dropna()
            if len(df15)<30 or len(df5)<30:
                time.sleep(30); continue
            if (df5['High'].iloc[-1]-df5['Low'].iloc[-1])>10:
                time.sleep(30); continue

            rh=df15['High'].iloc[-20:-1].max()
            rl=df15['Low'].iloc[-20:-1].min()
            c15=df15.iloc[-1]; p15=df15.iloc[-2]
           
