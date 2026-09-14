import os, time, threading, requests, yfinance as yf, pandas as pd, pytz
from flask import Flask
from datetime import datetime

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN", "8242504391:AAE...")
CHAT_ID = "7804217051"
EAT = pytz.timezone("Africa/Nairobi")

PAIRS = {
    "EURUSD=X": "EURUSD",
    "GBPUSD=X": "GBPUSD",
    "JPY=X": "USDJPY",
    "CHF=X": "USDCHF",
    "AUDUSD=X": "AUDUSD",
    "NZDUSD=X": "NZDUSD",
    "CAD=X": "USDCAD",
    "DX-Y.NYB": "DXY",
    "GC=F": "XAUUSD GOLD"
}

last = {k: 0 for k in PAIRS}
daily = {k: {"date": "", "count": 0} for k in PAIRS}

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except:
        pass

def get_signal(ticker, name):
    try:
        data = yf.download(ticker, period="5d", interval="15m", progress=False, auto_adjust=True)
        if data.empty or len(data) < 60:
            return None
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        close = data['Close']
        high = data['High']
        low = data['Low']
        sma20 = close.rolling(20).mean().iloc[-1]
        sma50 = close.rolling(50).mean().iloc[-1]
        recent_high = high.tail(60).max()
        recent_low = low.tail(60).min()
        curr = close.iloc[-1]
        is_bull = sma20 > sma50 and curr > recent_high * 0.999
        is_bear = sma20 < sma50 and curr < recent_low * 1.001
        if not (is_bull or is_bear):
            return None
        sh = high.tail(60).max()
        sl = low.tail(60).min()
        diff = sh - sl
        if diff == 0:
            return None
        fib50 = sh - diff*0.5
        fib62 = sh - diff*0.62
        fib70 = sh - diff*0.705
        fib79 = sh - diff*0.79
        direction = "BUY" if is_bull else "SELL"
        msg = f"🔥 *{name} {direction}* FIB 70.5%\n50%:{fib50:.5f} 70.5%:{fib70:.5f}\nENTRY {fib62:.5f}-{fib79:.5f}\nPrice {curr:.5f}"
        return msg
    except Exception as e:
        print(f"Error {name} {e}")
        return None

def loop():
    send("✅ Pavie SMC FIXED - No Syntax Error - Live")
    while True:
        try:
            now = datetime.now(EAT)
            if now.weekday() >= 5:
                time.sleep(600)
                continue
            for t, n in PAIRS.items():
                if time.time() - last[t] < 17280:
                    continue
                today = now.strftime("%Y-%m-%d")
                if daily[t]["date"]!= today:
                    daily[t] = {"date": today, "count": 0}
                if daily[t]["count"] >= 5:
                    continue
                sig = get_signal(t, n)
                if sig:
                    send(sig)
                    last[t] = time.time()
                    daily[t]["count"] += 1
            time.sleep(40)
        except Exception as e:
            print(f"Loop err {e}")
            time.sleep(60)

@app.route("/")
def home():
    return "Pavie LIVE FIXED"

@app.route("/testall")
def testall():
    send("🚀 PUSH LIVE TEST OK")
    return "ok"

threading.Thread(target=loop, daemon=True).start()
