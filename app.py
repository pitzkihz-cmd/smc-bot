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
def home(): return "GOLD WIN/LOSS TRACKER LIVE"

def send_telegram(text):
    try:
        for cid in [CHAT_ID, CHANNEL_ID]:
            if cid:
                requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": cid, "text": text, "parse_mode":"Markdown"}, timeout=10)
    except: pass

def get_price():
    df = yf.download("GC=F", period="1d", interval="1m", progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    return float(df['Close'].iloc[-1])

def bot_loop():
    active = None
    last_sent = {}
    wins = 0; losses = 0
    
    while True:
        try:
            tz = pytz.timezone("Africa/Nairobi")
            now = datetime.now(tz)
            h = now.hour + now.minute/60

            # --- TRACK ACTIVE TRADE ---
            if active:
                price = get_price()
                side = active['side']
                # TP1 BE alert
                if not active.get('be_done'):
                    tp1_trigger = (price <= active['tp1'] if side=="SELL" else price >= active['tp1'])
                    if tp1_trigger:
                        send_telegram(f"🔔 *BE ALERT*\n{side} TP1 hit at {active['tp1']:.1f} price now {price:.1f}\n👉 Move SL to Break-Even NOW!")
                        active['be_done']=True

                # Check WIN / LOSS
                hit_tp = (price <= active['tp3'] if side=="SELL" else price >= active['tp3'])
                hit_sl = (price >= active['sl3'] if side=="SELL" else price <= active['sl3'])

                if hit_tp:
                    wins+=1
                    send_telegram(f"✅ *WIN*\n{side} {active['strat']} CLOSED\nEntry {active['e2']:.1f} -> TP3 {active['tp3']:.1f}\nProfit +{abs(active['tp3']-active['e2']):.1f}$\n\nScore: {wins}W - {losses}L = {wins/(wins+losses)*100:.0f}%")
                    active=None
                elif hit_sl:
                    losses+=1
                    send_telegram(f"❌ *LOSS*\n{side} {active['strat']} STOPPED\nEntry {active['e2']:.1f} -> SL {active['sl3']:.1f}\nLoss -{abs(active['sl3']-active['e2']):.1f}$\n\nScore: {wins}W - {losses}L\nNext will win 💪")
                    active=None

                time.sleep(10); continue

            # --- FIND NEW ENTRY ---
            if not (10 <= h <= 23.5): time.sleep(30); continue

            df15 = yf.download("GC=F", period="5d", interval="15m", progress=False)
            df5 = yf.download("GC=F", period="5d", interval="5m", progress=False)
            if isinstance(df15.columns, pd.MultiIndex): df15.columns = df15.columns.get_level_values(0)
            if isinstance(df5.columns, pd.MultiIndex): df5.columns = df5.columns.get_level_values(0)
            
            if (df5['High'].iloc[-1]-df5['Low'].iloc[-1]) > 10: time.sleep(30); continue

            rh, rl = df15['High'].iloc[-20:-1].max(), df15['Low'].iloc[-20:-1].min()
            c15, p15 = df15.iloc[-1], df15.iloc[-2]

            signal=None
            if c15['Close']>rh and p15['Close']<rh and df15['Low'].iloc[-1]<rl and df5['Low'].iloc[-1]>df5['High'].iloc[-3]:
                signal=("BUY","BOS+Sweep",rl,rh)
            if c15['Close']<rl and p15['Close']>rl and df15['High'].iloc[-1]>rh and df5['High'].iloc[-1]<df5['Low'].iloc[-3]:
                signal=("SELL","BOS+Sweep",rh,rl)
            if not signal and 15.5<=h<=17.5:
                if df5['Low'].iloc[-1]>df5['High'].iloc[-3]: signal=("BUY","Silver Bullet",df5['Low'].iloc[-1],rh)
                if df5['High'].iloc[-1]<df5['Low'].iloc[-3]: signal=("SELL","Silver Bullet",df5['High'].iloc[-1],rl)

            if not signal: time.sleep(20); continue

            side,strat,sweep,bos = signal
            key=f"{side}-{int(sweep)}"
            if key in last_sent and time.time()-last_sent[key] < 900: time.sleep(20); continue

            rng=abs(bos-sweep)
            if side=="BUY":
                e1,sl1,e2,sl2,e3,sl3,tp1,tp2,tp3 = sweep+rng*0.5,sweep-1.5,sweep+rng*0.62,sweep-0.5,sweep+rng*0.79,sweep+rng*0.79-1.2,sweep+rng*0.9,bos+rng*1.2,bos+rng*1.8
            else:
                e1,sl1,e2,sl2,e3,sl3,tp1,tp2,tp3 = sweep-rng*0.5,sweep+1.5,sweep-rng*0.62,sweep+0.5,sweep-rng*0.79,sweep-rng*0.79+1.2,sweep-rng*0.9,bos-rng*1.2,bos-rng*1.8

            msg=f"""
🔥 *GOLD {side} | {strat}*
{now.strftime('%H:%M EAT')} | Score {wins}W-{losses}L

📍 E1 `{e1:.1f}` SL `{sl1:.1f}`
📍 E2 `{e2:.1f}` SL `{sl2:.1f}` MAIN
📍 E3 `{e3:.1f}` SL `{sl3:.1f}`
🎯 TP1 `{tp1:.1f}` BE
🎯 TP2 `{tp2:.1f}`
🎯 TP3 `{tp3:.1f}` RUNNER
"""
            send_telegram(msg)
            active={"side":side,"strat":strat,"e2":e2,"sl3":sl3,"tp1":tp1,"tp3":tp3,"be_done":False}
            last_sent[key]=time.time()
            time.sleep(90)

        except Exception as e:
            print(e); time.sleep(30)

threading.Thread(target=bot_loop, daemon=True).start()

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
