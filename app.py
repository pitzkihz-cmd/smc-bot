import os, time, threading, requests, yfinance as yf, pandas as pd, pytz
from flask import Flask
from datetime import datetime

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
CHAT_ID = "7804217051"
EAT = pytz.timezone("Africa/Nairobi")

PAIRS = {
    "EURUSD=X": "EURUSD",
    "GBPUSD=X": "GBPUSD",
    "JPY=X": "USDJPY",
    "GC=F": "XAUUSD GOLD",
    "DX-Y.NYB": "DXY"
}

last = {k: 0 for k in PAIRS}

def send(msg):
    if not BOT_TOKEN or len(BOT_TOKEN) < 40:
        print("BAD TOKEN len", len(BOT_TOKEN))
        return False
    try:
        url = "https://api.telegram.org/bot{}/sendMessage".format(BOT_TOKEN)
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=15)
        print("SEND", r.status_code, r.text[:200])
        return r.status_code == 200
    except Exception as e:
        print("SEND FAIL", e)
        return False

def get_signal(ticker, name):
    try:
        data = yf.download(ticker, period="2d", interval="15m", progress=False, auto_adjust=True)
        if data.empty or len(data) < 30:
            return None
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        close = data['Close']
        high = data['High']
        low = data['Low']
        curr = float(close.iloc[-1])
        sma20 = float(close.rolling(20).mean().iloc[-1])
        sh = float(high.tail(40).max())
        sl = float(low.tail(40).min())
        diff = sh - sl
        if diff == 0:
            return None
        fib50 = sh - diff*0.5
        fib62 = sh - diff*0.618
        fib705 = sh - diff*0.705
        fib79 = sh - diff*0.79

        dist_705 = ((curr - fib705)/curr)*100
        dist_50 = ((curr - fib50)/curr)*100
        fib_pos = ((sh - curr)/diff)*100
        direction = "BUY" if curr > sma20 else "SELL"

        if 60 <= fib_pos <= 80:
            win = 82
        elif 50 <= fib_pos <= 85:
            win = 75
        else:
            win = 62

        sl_price = sl if direction == "BUY" else sh
        sl_pct = ((sl_price - curr)/curr)*100

        # Build msg without broken f-strings
        msg = "🔥 *{} {} | {}% WIN*\n\n".format(name, direction, win)
        msg += "Price: `{:.5f}`\n".format(curr)
        msg += "Fib Pos: `{:.1f}%` (Target 70.5%)\n\n".format(fib_pos)
        msg += "FIB %:\n50%: `{:.5f}` ({:+.2f}%)\n".format(fib50, dist_50)
        msg += "70.5%: `{:.5f}` ({:+.2f}%) BEST\n".format(fib705, dist_705)
        msg += "\nENTRY TO PLACE:\n`{:.5f}` to `{:.5f}`\n".format(fib62, fib79)
        msg += "Dist NOW: `{:+.2f}%` to 70.5%\n\n".format(dist_705)
        msg += "SL: `{:.5f}` ({:+.2f}%)\n".format(sl_price, sl_pct)
        msg += "Time: {} EAT".format(datetime.now(EAT).strftime('%H:%M'))
        return msg
    except Exception as e:
        print("Error", name, e)
        return None

def loop():
    send("✅ Pavie BOT FIXED - % MODE LIVE")
    while True:
        try:
            for t, n in PAIRS.items():
                if time.time() - last[t] < 900:
                    continue
                sig = get_signal(t, n)
                if sig:
                    if send(sig):
                        last[t] = time.time()
            time.sleep(60)
        except Exception as e:
            print("Loop err", e)
            time.sleep(60)

@app.route("/")
def home():
    return "Pavie LIVE token_len={}".format(len(BOT_TOKEN))

@app.route("/testall")
def testall():
    ok = send("🚀 TEST OK - FIXED VERSION")
    return "sent={} token_len={}".format(ok, len(BOT_TOKEN))

@app.route("/forcesignal")
def forcesignal():
    for t, n in PAIRS.items():
        sig = get_signal(t, n)
        if sig:
            send(sig)
            return "FORCED {}".format(n)
    return "failed"

threading.Thread(target=loop, daemon=True).start()
