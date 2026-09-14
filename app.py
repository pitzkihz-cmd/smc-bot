import os, time, threading, requests, yfinance as yf, pandas as pd, pytz
from flask import Flask
from datetime import datetime

app = Flask(__name__)

# FULL TOKEN FROM RENDER ENV - NO ... !
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
if len(BOT_TOKEN) < 40:
    print(f"ERROR: BOT_TOKEN TOO SHORT len={len(BOT_TOKEN)} - PASTE FULL TOKEN FROM BOTFATHER!")

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

def send(msg):
    if not BOT_TOKEN or len(BOT_TOKEN) < 40:
        print(f"CANNOT SEND - TOKEN BAD len={len(BOT_TOKEN)}")
        return False
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=15)
        print(f"SEND {r.status_code} {r.text[:300]}")
        return r.status_code == 200
    except Exception as e:
        print(f"SEND FAIL {e}")
        return False

def get_signal(ticker, name):
    try:
        data = yf.download(ticker, period="2d", interval="15m", progress=False, auto_adjust=True)
        if data.empty or len(data) < 30: return None
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
        if diff == 0 or curr == 0: return None
        fib50 = sh - diff*0.5
        fib62 = sh - diff*0.618
        fib705 = sh - diff*0.705
        fib79 = sh - diff*0.79
        dist_to_705 = ((curr - fib705)/curr)*100
        dist_to_50 = ((curr - fib50)/curr)*100
        zone_width_pct = ((fib62 - fib79)/curr)*100
        fib_position = ((sh - curr)/diff)*100
        direction = "BUY" if curr > sma20 else "SELL"
        win_pct = 82 if 60 <= fib_position <= 80 else 75 if 50 <= fib_position <= 85 else 62
        sl_price = sl if direction=="BUY" else sh
        sl_pct = ((sl_price - curr)/curr)*100
        tp1 = curr + abs(curr-sl_price)*1.5 if direction=="BUY" else curr - abs(curr-sl_price)*1.5
        tp2 = curr + abs(curr-sl_price)*2.8 if direction=="BUY" else curr - abs(curr-sl_price)*2.8
        tp1_pct = ((tp1 - curr)/curr)*100
        tp2_pct = ((tp2 - curr)/curr)*100
        msg = (
            f"🔥 *{name} {direction} | {win_pct}% WIN*\n\n"
            f"💰 Price: `{curr:.5f}`\n"
            f"📊 Fib Pos: `{fib_position:.1f}%` (Target 70.5%)\n\n"
            f"🎯 *FIB %:*\n"
            f"50%: `{fib50:.
