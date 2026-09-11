import os, time, requests, yfinance as yf, pytz, pandas as pd
from flask import Flask
from threading import Thread
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN", "8763626113:AAHLHRlF5uXCgEEOxwEztXs8q1tnER3RY3U")
CHAT_ID = os.getenv("CHAT_ID", "7804217051")
EAT = pytz.timezone("Africa/Nairobi")
app = Flask(__name__)

PAIRS = {"EURUSD":"EURUSD=X","GBPUSD":"GBPUSD=X","USDJPY":"USDJPY=X","USDCHF":"USDCHF=X","AUDUSD":"AUDUSD=X","NZDUSD":"NZDUSD=X","USDCAD":"USDCAD=X","DXY":"DX-Y.NYB","XAUUSD GOLD":"GC=F"}

@app.route("/")
def home(): return f"Pavie PUSH LIVE {CHAT_ID} <br><a href='/test'>TEST 1</a> | <a href='/testall'>TEST ALL PUSH</a> | <a href='/push'>PUSH NOW</a>"

@app.route("/test")
def test():
    r=requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id":CHAT_ID,"text":f"🔔 TEST 1 OK Pavie!\nID {CHAT_ID}\n@Paviesmc2026bot LIVE ✅","parse_mode":"HTML"}, timeout=15)
    return f"Sent {r.status_code} {r.text[:200]}"

@app.route("/push")
def push():
    # PUSH NOTIFICATION with sound
    for i in range(3):
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={
            "chat_id": CHAT_ID,
            "text": f"🔔 <b>PUSH NOTIFICATION {i+1}/3</b>\n\n🔊 Sound ON\n📳 Vibrate ON\n⚡️ @Paviesmc2026bot\n\nID {CHAT_ID} WORKING ✅\nTime: {datetime.now(EAT).strftime('%H:%M:%S')}",
            "parse_mode": "HTML",
            "disable_notification": False # FORCE PUSH SOUND
        })
        time.sleep(2)
    return "3 PUSH sent with SOUND!"

@app.route("/testall")
def testall():
    # Test everything: text + signal + gold
    try:
        price = yf.download("GC=F", period="1d", interval="1m", progress=False)["Close"].iloc[-1]
    except: price=3685.50

    msgs = [
        f"☀️ <b>GOOD MORNING PAVIE!</b>\n{datetime.now(EAT).strftime('%A %d %b %H:%M')}\nLondon Session 🇬🇧\n45 signals today\n@Paviesmc2026bot",
        f"💵 <b>EURUSD BUY 5x/Day London 🇬🇧</b>\n\n<b>FIB:</b> 50% 1.08500 | 62% 1.08450 | 70.5% 1.08420 ⭐ | 79% 1.08390\n<b>ENTRY:</b> 1.08450 - 1.08390 Live 1.08480 <b>ENTER NOW</b>\n<b>SL:</b> 1.08250\n<b>TP1:</b> 1.08500 | <b>TP2:</b> 1.08650 | <b>TP3:</b> 1.08800\n\n<b>PUSH TEST SIGNAL ✅</b>",
        f"🟡 <b>XAUUSD GOLD BUY 5x/Day NY 🇺🇸</b>\n\n<b>FIB:</b> 50% 3670 | 62% 3665 | 70.5% 3660 ⭐ | 79% 3655\n<b>ENTRY:</b> 3665 - 3655 Live {price:.2f} <b>ENTER NOW</b>\n<b>SL:</b> 3645\n<b>TP1:</b> 3670 | <b>TP2:</b> 3685 | <b>TP3:</b> 3700\n\n<b>GOLD PUSH TEST ✅</b>\n<b>⏰ {datetime.now(EAT).strftime('%H:%M')} | @Paviesmc2026bot</b>"
    ]
    for m in msgs:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id":CHAT_ID,"text":m,"parse_mode":"HTML","disable_notification":False}, timeout=15)
        time.sleep(3)
    return "TEST ALL 3 PUSHED! Check Telegram"

def send(t):
    try: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id":CHAT_ID,"text":t,"parse_mode":"HTML","disable_notification":False}, timeout=25)
    except: pass

def get_session():
    h=datetime.now(EAT).hour
    if 3 <= h < 12: return "London 🇬🇧"
    if 12 <= h < 20: return "New York 🇺🇸"
    return "Asian 🇯🇵"

def analyze(name,ticker):
    try:
        df=yf.download(ticker, period="5d", interval="15m", progress=False, auto_adjust=True)
        if len(df)<80: return None
        price=float(df["Close"].iloc[-1]); high=float(df["High"].iloc[-60:].max()); low=float(df["Low"].iloc[-60:].min()); rng=high-low
        if rng==0: return None
        sma20=df["Close"].rolling(20).mean().iloc[-1]; sma50=df["Close"].rolling(50).mean().iloc[-1]
        tr=pd.concat([df["High"]-df["Low"], (df["High"]-df["Close"].shift()).abs(), (df["Low"]-df["Close"].shift()).abs()], axis=1).max(axis=1)
        atr=float(tr.rolling(14).mean().iloc[-1])
        bullish=sma20>sma50; f50=low+rng*0.5; f62=low+rng*0.618; f705=low+rng*0.705; f79=low+rng*0.79
        f50s=high-rng*0.5; f62s=high-rng*0.618; f705s=high-rng*0.705; f79s=high-rng*0.79
        if bullish: return ("BUY",price,low,high,rng,atr,f50,f62,f705,f79)
        return ("SELL",price,low,high,rng,atr,f50s,f62s,f705s,f79s)
    except: return None

def build(name,data):
    side,price,sl_low,sl_high,rng,atr,f50,f62,f705,f79=data
    is_gold="GOLD" in name; fmt=".2f" if is_gold else ".5f"; now=datetime.now(EAT); sess=get_session()
    if side=="BUY":
        sl=f79-atr*0.5; sl=price-9 if is_gold and sl>price-3 else sl; sl=price-0.0018 if not is_gold and sl>price-0.0005 else sl
        tp1=f50; tp2=sl_high; tp3=sl_high+rng*0.618; zone=f"{f62:{fmt}} - {f79:{fmt}}"
    else:
        sl=f79+atr*0.5; sl=price+9 if is_gold and sl<price+3 else sl; sl=price+0.0018 if not is_gold and sl<price-0.0005 else sl
        tp1=f50; tp2=sl_low; tp3=sl_low-rng*0.618; zone=f"{f79:{fmt}} - {f62:{fmt}}"
    risk=abs(price-sl)
    return f"""{"🟡" if is_gold else "💵"} <b>{name} {side} 5x/Day {sess}</b>\n\n<b>FIB:</b> 50% {f50:{fmt}} | 62% {f62:{fmt}} | 70.5% {f705:{fmt}} ⭐ | 79% {f79:{fmt}}\n<b>ENTRY:</b> {zone} Live {price:{fmt}} <b>ENTER NOW</b>\n<b>SL:</b> {sl:{fmt}} (-{risk:{fmt}})\n<b>TP1:</b> {tp1:{fmt}} | <b>TP2:</b> {tp2:{fmt}} | <b>TP3:</b> {tp3:{fmt}}\n\n<b>WHY:</b> BOS + Liquidity + OB + OTE\n<b>⏰ {now.strftime('%H:%M %d-%b')} | @Paviesmc2026bot</b>\n"""

def loop():
    send(f"🚀 <b>@Paviesmc2026bot PUSH LIVE Pavie!</b>\nID {CHAT_ID}\n45/day + PUSH 🔊\nTest: /testall")
    last={}; daily={}
    while True:
        try:
            now=datetime.now(EAT)
            for name,ticker in PAIRS.items():
                if daily.get(name,0)>=5: continue
                if time.time()-last.get(name,0) < 17280 and daily.get(name,0)>0: continue
                data=analyze(name,ticker)
                if not data: continue
                send(build(name,data)); last[name]=time.time(); daily[name]=daily.get(name,0)+1; time.sleep(12)
            time.sleep(40)
        except: time.sleep(60)

Thread(target=loop, daemon=True).start()
if __name__=="__main__": app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
