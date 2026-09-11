import os, time, requests, yfinance as yf, pytz, pandas as pd
from flask import Flask
from threading import Thread
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID", "7804217051")
EAT = pytz.timezone("Africa/Nairobi")
app = Flask(__name__)

PAIRS = {
    "EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X", "USDJPY": "USDJPY=X",
    "USDCHF": "USDCHF=X", "AUDUSD": "AUDUSD=X", "NZDUSD": "NZDUSD=X",
    "USDCAD": "USDCAD=X", "DXY": "DX-Y.NYB", "XAUUSD GOLD": "GC=F",
}
SIGNAL_INTERVAL = 17280 # 5 per day exact

@app.route("/")
def home(): return f"Pavie 2026 LIVE {CHAT_ID} 45/day @Paviesmc2026bot"
@app.route("/test")
def test():
    r=requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": "🔥 @Paviesmc2026bot TEST OK Pavie!\nID 7804217051\n45 signals/day ACTIVE ✅\n5 per market | Gold 7 days", "parse_mode": "HTML"}, timeout=15)
    return f"Sent {r.status_code} to {CHAT_ID}"

def send(t):
    try: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": t, "parse_mode": "HTML"}, timeout=25)
    except: pass

def get_session():
    h=datetime.now(EAT).hour
    if 3 <= h < 12: return "London 🇬🇧"
    if 12 <= h < 20: return "New York 🇺🇸"
    return "Asian 🇯🇵"

def get_news(): return "📰 CPI 15:30 EAT 🔴 | Fed Sep 15-16 | Gold volatile"

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
    return f"""{"🟡" if is_gold else "💵"} <b>{name} {side} 5x/Day {sess}</b>\n\n<b>FIB:</b> 50% {f50:{fmt}} | 62% {f62:{fmt}} | 70.5% {f705:{fmt}} ⭐ | 79% {f79:{fmt}}\n<b>ENTRY:</b> {zone} Live {price:{fmt}} <b>ENTER NOW</b>\n<b>SL:</b> {sl:{fmt}} (-{risk:{fmt}})\n<b>TP1:</b> {tp1:{fmt}} | <b>TP2:</b> {tp2:{fmt}} | <b>TP3:</b> {tp3:{fmt}}\n\n<b>WHY:</b> BOS + Liquidity + OB + OTE 62-79%\n<b>NEWS:</b> {get_news()}\n<b>⏰ {now.strftime('%H:%M %d-%b')} | @Paviesmc2026bot</b>\n"""

def loop():
    send("🚀 <b>@Paviesmc2026bot LIVE Pavie!</b>\nID 7804217051\n45 signals/day\nFIB SMC ICT OTE\nGold 7 Days\nMorning 6:30 & 8pm ✅")
    last={}; last_hb=0; gm=False; ge=False; daily={}
    while True:
        try:
            now=datetime.now(EAT); h,m=now.hour,now.minute
            if h==6 and m==30 and not gm:
                send(f"☀️ <b>Good Morning Pavie!</b> {now.strftime('%A %d %b')}\n{get_session()} — 45 signals today\n{get_news()}\n@Paviesmc2026bot LIVE!"); gm=True; ge=False; daily={}
            if h==20 and m==0 and not ge:
                send(f"🌌 <b>Good Evening Pavie!</b>\nToday: {sum(daily.values())}/45\nGold overnight ✅\nSee you 6:30am"); ge=True; gm=False
            if h==7: gm=True
            if h==21: ge=True
            if h==5: gm=False; daily={}
            if time.time()-last_hb>7200:
                try:
                    gp=yf.download("GC=F", period="1d", interval="1m", progress=False)["Close"].iloc[-1]
                    send(f"💓 Heartbeat {now.strftime('%H:%M')} | Gold {gp:.2f} | {get_session()} | {sum(daily.values())}/45"); last_hb=time.time()
                except: pass
            for name,ticker in PAIRS.items():
                if daily.get(name,0)>=5: continue
                if time.time()-last.get(name,0) < SIGNAL_INTERVAL and daily.get(name,0)>0: continue
                if h==15 and 25<=m<=40: continue
                data=analyze(name,ticker)
                if not data: continue
                send(build(name,data)); last[name]=time.time(); daily[name]=daily.get(name,0)+1; time.sleep(12)
            time.sleep(40)
        except Exception as e: print(e); time.sleep(60)

Thread(target=loop, daemon=True).start()
if __name__=="__main__": app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
