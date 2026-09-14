import os, time, threading, requests, yfinance as yf, pandas as pd, pytz
from flask import Flask
from datetime import datetime

app = Flask(__name__)

# <<< PASTE YOUR FULL TOKEN HERE - REPLACE THIS LINE >>>
BOT_TOKEN = "8242504391:AAE_PASTE_REST_HERE_46_CHARS_TOTAL"
# Example how long: 8242504391:AAElr1c2x3y4z5a6b7c8d9e0f1g2h3i4j5k

CHAT_ID = "7804217051"
EAT = pytz.timezone("Africa/Nairobi")

PAIRS = {"EURUSD=X":"EURUSD","GBPUSD=X":"GBPUSD","JPY=X":"USDJPY","GC=F":"XAUUSD GOLD","DX-Y.NYB":"DXY"}
last = {k:0 for k in PAIRS}

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode":"Markdown"}, timeout=15)
        print("SEND", r.status_code, r.text[:200])
        return r.status_code==200
    except Exception as e:
        print(e)
        return False

def get_signal(ticker,name):
    try:
        data=yf.download(ticker,period="2d",interval="15m",progress=False,auto_adjust=True)
        if data.empty or len(data)<30: return None
        if isinstance(data.columns,pd.MultiIndex): data.columns=data.columns.get_level_values(0)
        close=data['Close']; high=data['High']; low=data['Low']
        curr=float(close.iloc[-1]); sma=float(close.rolling(20).mean().iloc[-1])
        sh=float(high.tail(40).max()); sl=float(low.tail(40).min())
        diff=sh-sl
        if diff==0: return None
        fib50=sh-diff*0.5; fib62=sh-diff*0.618; fib705=sh-diff*0.705; fib79=sh-diff*0.79
        dist=((curr-fib705)/curr)*100; fib_pos=((sh-curr)/diff)*100
        direction="BUY" if curr>sma else "SELL"
        win=82 if 60<=fib_pos<=80 else 75
        sl_price=sl if direction=="BUY" else sh
        msg="🔥 *{} {} | {}% WIN*\nPrice: `{:.5f}`\nFib: `{:.1f}%`\nENTRY: `{:.5f}` to `{:.5f}`\nDist: `{:+.2f}%` to 70.5%\nSL: `{:.5f}`".format(name,direction,win,curr,fib_pos,fib62,fib79,dist,sl_price)
        return msg
    except: return None

def loop():
    send("✅ FULL BOT LIVE - TOKEN OK")
    while True:
        for t,n in PAIRS.items():
            if time.time()-last[t]<900: continue
            sig=get_signal(t,n)
            if sig and send(sig): last[t]=time.time()
        time.sleep(60)

@app.route("/")
def home(): return f"FULL LIVE token_len={len(BOT_TOKEN)}"

@app.route("/testall")
def testall():
    ok=send("🚀 FULL TEST OK")
    return f"sent={ok} token_len={len(BOT_TOKEN)}"

threading.Thread(target=loop,daemon=True).start()
