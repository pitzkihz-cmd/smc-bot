from flask import Flask
import os, threading, time, requests, pytz
from datetime import datetime
import yfinance as yf
import pandas as pd

# ===== PASTE YOUR TOKENS HERE DIRECTLY =====
BOT_TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE" # example: 123456:AAHxyz...
CHAT_ID = "PASTE_YOUR_CHAT_ID_HERE" # example: 123456789
CHANNEL_ID = "PASTE_YOUR_CHANNEL_ID_HERE" # example: -100123456 or same as CHAT_ID
# ===========================================

app = Flask(__name__)

@app.route('/')
def home(): return "GOLD BOT LIVE - Full Package"

@app.route('/test')
def test():
    ok = send_telegram("✅ *TEST OK*\nGold Bot Live - Full Package Working")
    return f"Telegram send status: {ok} - Check Telegram now. Token set: {BOT_TOKEN[:10]}..."

def send_telegram(text):
    try:
        sent=False
        for cid in [CHAT_ID, CHANNEL_ID]:
            if cid and BOT_TOKEN and "PASTE" not in BOT_TOKEN:
                r=requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id":cid,"text":text,"parse_mode":"Markdown"}, timeout=15)
                print(f"Telegram to {cid}: {r.status_code} {r.text}")
                if r.status_code==200: sent=True
        return sent
    except Exception as e:
        print(f"Telegram error: {e}")
        return str(e)

def get_price():
    df = yf.download("GC=F", period="1d", interval="1m", progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    return float(df['Close'].iloc[-1])

def bot_loop():
    active=None; last_sent={}; wins=0; losses=0
    print("FULL BOT STARTED")
    time.sleep(8)
    send_telegram("🚀 *GOLD BOT ONLINE - FULL PACKAGE*\nUnlimited + BE + Win/Loss\nScanning...")
    while True:
        try:
            tz=pytz.timezone("Africa/Nairobi"); now=datetime.now(tz); h=now.hour+now.minute/60
            if active:
                price=get_price(); side=active['side']
                if not active.get('be_done'):
                    if (price<=active['tp1'] if side=="SELL" else price>=active['tp1']):
                        send_telegram(f"🔔 *BE ALERT*\n{side} TP1 {active['tp1']:.1f} hit! Move SL to BE!")
                        active['be_done']=True
                if (price<=active['tp3'] if side=="SELL" else price>=active['tp3']):
                    wins+=1; send_telegram(f"✅ *WIN +{abs(active['tp3']-active['e2']):.1f}$*\nScore {wins}W-{losses}L"); active=None
                elif (price>=active['sl'] if side=="SELL" else price<=active['sl']):
                    losses+=1; send_telegram(f"❌ *LOSS*\nScore {wins}W-{losses}L"); active=None
                time.sleep(15); continue
            if not (10<=h<=23.5): time.sleep(60); continue
            df15=yf.download("GC=F", period="5d", interval="15m", progress=False, auto_adjust=True)
            df5=yf.download("GC=F", period="5d", interval="5m", progress=False, auto_adjust=True)
            if isinstance(df15.columns, pd.MultiIndex): df15.columns=df15.columns.get_level_values(0)
            if isinstance(df5.columns, pd.MultiIndex): df5.columns=df5.columns.get_level_values(0)
            df15=df15.dropna(); df5=df5.dropna()
            if len(df15)<30 or len(df5)<30: time.sleep(30); continue
            if (df5['High'].iloc[-1]-df5['Low'].iloc[-1])>10: time.sleep(30); continue
            rh=df15['High'].iloc[-20:-1].max(); rl=df15['Low'].iloc[-20:-1].min()
            c15=df15.iloc[-1]; p15=df15.iloc[-2]; signal=None
            if c15['Close']>rh and p15['Close']<rh and df5['Low'].iloc[-1]>df5['High'].iloc[-3]: signal=("BUY","BOS+Sweep",rl,rh)
            if c15['Close']<rl and p15['Close']>rl and df5['High'].iloc[-1]<df5['Low'].iloc[-3]: signal=("SELL","BOS+Sweep",rh,rl)
            if not signal and 15.5<=h<=17.5:
                if df5['Low'].iloc[-1]>df5['High'].iloc[-3]: signal=("BUY","Silver Bullet",df5['Low'].iloc[-1],rh)
                if df5['High'].iloc[-1]<df5['Low'].iloc[-3]: signal=("SELL","Silver Bullet",df5['High'].iloc[-1],rl)
            if not signal: time.sleep(20); continue
            side,strat,sweep,bos=signal; key=f"{side}-{int(sweep)}"
            if key in last_sent and time.time()-last_sent[key]<900: time.sleep(20); continue
            rng=abs(bos-sweep)
            if side=="BUY": e2=sweep+rng*0.62; sl=sweep-0.5; tp1=sweep+rng*0.9; tp3=bos+rng*1.8; e1=sweep+rng*0.5; e3=sweep+rng*0.79
            else: e2=sweep-rng*0.62; sl=sweep+0.5; tp1=sweep-rng*0.9; tp3=bos-rng*1.8; e1=sweep-rng*0.5; e3=sweep-rng*0.79
            msg=f"🔥 *GOLD {side} | {strat}*\n{now.strftime('%H:%M EAT')} | {wins}W-{losses}L\n📍 E1 `{e1:.1f}`\n📍 E2 `{e2:.1f}` MAIN\n📍 E3 `{e3:.1f}`\nSL `{sl:.1f}`\n🎯 TP1 `{tp1:.1f}` BE\n🎯 TP3 `{tp3:.1f}`"
            send_telegram(msg); active={"side":side,"strat":strat,"e2":e2,"sl":sl,"tp1":tp1,"tp3":tp3,"be_done":False}; last_sent[key]=time.time(); time.sleep(90)
        except Exception as e: print(e); time.sleep(30)

threading.Thread(target=bot_loop, daemon=True).start()
