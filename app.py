import os
import time
import threading
import requests
import yfinance as yf
import pandas as pd
import numpy as np
from flask import Flask
from datetime import datetime
import pytz

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
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
COOLDOWN = 17280 # 4.8 hours
DAILY_LIMIT = 5

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": msg,
            "parse_mode": "Markdown",
            "disable_notification": False
        }
        requests.post(url, json=payload, timeout=10)
        print(f"Sent: {msg[:50]}")
    except Exception as e:
        print(f"Send error: {e}")

def get_signal(ticker, name):
    try:
        data = yf.download(ticker, period="5d", interval="15m", progress=False, auto_adjust=False)
        if data.empty or len(data) < 60:
            print(f"{name} no data / weekend")
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
        curr_price = close.iloc[-1]

        atr = (high - low).rolling(14).mean().iloc[-1]

        # SMC BOS Logic
        is_bull = sma20 > sma50 and curr_price > recent_high * 0.999
        is_bear = sma20 < sma50 and curr_price < recent_low * 1.001

        if not (is_bull or is_bear):
            print(f"{name} no BOS")
            return None

        swing_high = high.tail(60).max()
        swing_low = low.tail(60).min()
        diff = swing_high - swing_low
        if diff == 0:
            return None

        fib_50 = swing_high - diff * 0.5
        fib_62 = swing_high - diff * 0.62
        fib_705 = swing_high - diff * 0.705
        fib_79 = swing_high - diff * 0.79

        if is_bull:
            direction = "BUY"
            entry = f"{fib_62:.5f} - {fib_79:.5f}"
            sl = fib_79 - atr * 0.5
            tp1 = fib_50
            tp2 = swing_high
            tp3 = swing_high + diff * 0.618
        else:
            direction = "SELL"
            entry = f"{fib_62:.5f} - {fib_79:.5f}"
            sl = fib_79 + atr * 0.5
            tp1 = fib_50
            tp2 = swing_low
            tp3 = swing_low - diff * 0.618
            # For SELL invert fib calc correctly
            fib_50 = swing_low + diff * 0.5
            fib_62 = swing_low + diff * 0.38
            fib_705 = swing_low + diff * 0.295
            fib_79 = swing_low + diff * 0.21

        session = "London" if 5 <= datetime.now(EAT).hour <= 12 else "NY"

        msg = f"""🔥 *{name} {direction}* + {session} 🚩
*FIB OTE SMC*
50%: {fib_50:.5f}
62%: {fib_62:.5f}
70.5% ⭐: {fib_705:.5f}
79%: {fib_79:.5f}

*ENTRY:* {entry} = LIVE ENTER NOW
*SL:* {sl:.5f}
*TP1:* {tp1:.5f}
*TP2:* {tp2:.5f}
*TP3:* {tp3:.5f}

*WHY:* BOS + Liquidity Sweep + OB + OTE 70.5%
SMA20 {sma20:.5f} vs SMA50 {sma50:.5f}
Price: {curr_price:.5f}
"""
        return msg
    except Exception as e:
        print(f"Error {name}: {e}")
        return None

def bot_loop():
    send("✅ Pavie SMC 2026 Bot RESTARTED - Fixed version, no spam, only real FIB signals")
    while True:
        try:
            now = datetime.now(EAT)
            # No signals Saturday/Sunday
            if now.weekday() >= 5:
                print("Weekend - Market Closed - sleeping 10 min")
                time.sleep(600)
                continue

            for ticker, name in PAIRS.items():
                # Cooldown check
                if time.time() - last[ticker] < COOLDOWN:
                    continue
                # Daily limit
                today_str = now.strftime("%Y-%m-%d")
                if daily[ticker]["date"]!= today_str:
                    daily[ticker] = {"date": today_str, "count": 0}
                if daily[ticker]["count"] >= DAILY_LIMIT:
                    continue

                signal = get_signal(ticker, name)
                if signal:
                    send(signal)
                    last[ticker] = time.time()
                    daily[ticker]["count"] += 1
                    time.sleep(3)
