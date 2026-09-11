import yfinance as yf, requests, os, time, threading
from datetime import datetime
import pytz
import matplotlib
matplotlib.use('Agg')
import mplfinance as mpf
from flask import Flask

TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
EAT = pytz.timezone("Africa/Nairobi")

SYMBOLS = {
    "XAUUSD.s": {"yf": "GC=F", "offset": -12.5, "emoji": "🔥 GOLD", "dec": 1},
    "BTCUSD": {"yf": "BTC-USD", "offset": 0, "emoji": "₿ BTC", "dec": 1},
    "EURUSD": {"yf": "EURUSD=X", "offset": 0, "emoji": "💶 EURUSD", "dec": 5}
}

def send_text(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try: requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except: pass

def send_entry(sym, cfg, df, f70, f79, f88, sl, tp1, tp3, price):
    try:
        plot_df = df.tail(80).copy()
        path = f"/tmp/{sym.replace('.','_')}.png"
        hlines = dict(hlines=[f70, f79, f88, sl], colors=['#ff9800','#00c853','#ff1744','#ff1744'], linestyle='--')
        mpf.plot(plot_df, type='candle', style='yahoo', title=f"{sym} LIVE BUY {price:.{cfg['dec']}f}",
                 ylabel='Price', hlines=hlines, volume=False,
                 savefig=dict(fname=path, dpi=150, bbox_inches='tight'))
        caption = f"{cfg['emoji']} {sym} LIVE BUY\n{datetime.now(EAT).strftime('%H:%M EAT')} NOW {price:.{cfg['dec']}f}\nE2 {f79:.{cfg['dec']}f} SL {sl:.{cfg['dec']}f}"
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        with open(path, 'rb') as ph:
            requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"photo": ph}, timeout=20)
    except Exception as e:
        print(f"chart err {e}")

def get_data(cfg):
    try:
        df = yf.Ticker(cfg['yf']).history(period="1d", interval="5m")
        if df.empty: return None, None
        for c in ['Open','High','Low','Close']: df[c] += cfg['offset']
        return df['Close'].iloc[-1], df
    except: return None, None

def bot_loop():
    active = {}
    send_text("✅ LIVE BOT 24/7 STARTED | All sessions | TP AFTER hit only")
    while True:
        try:
            for sym, cfg in SYMBOLS.items():
                price, df = get_data(cfg)
                if price is None: continue
                if sym not in active:
                    low = df['Low'].tail(100).min()
                    high = df['High'].tail(100).max()
                    rng = high - low
                    if rng==0: continue
                    f61 = high - rng*0.618
                    f70 = high - rng*0.70
                    f79 = high - rng*0.79
                    f88 = high - rng*0.88
                    if price > f61: continue
                    if f88 < price < f70:
                        sl = low - rng*0.05
                        tp1 = high
                        tp3 = high + rng*0.5
                        send_entry(sym, cfg, df, f70, f79, f88, sl, tp1, tp3, price)
                        active[sym] = {"tp1": tp1, "tp3": tp3, "sl": sl, "entry": price, "f79": f79}
                else:
                    t = active[sym]
                    if price <= t['sl']:
                        send_text(f"❌ {sym} SL HIT LIVE\nEntry {t['entry']:.{cfg['dec']}f} -> {price:.{cfg['dec']}f}")
                        del active[sym]
                    elif price >= t['tp3']:
                        send_text(f"✅ {sym} TP3 HIT LIVE WIN\n+{t['tp3']-t['f79']:.{cfg['dec']}f} | NOW {price:.{cfg['dec']}f}")
                        del active[sym]
                    elif price >= t['tp1'] and t['tp1']!=999999:
                        send_text(f"🔔 {sym} TP1 HIT LIVE -> BE\nNOW {price:.{cfg['dec']}f}")
                        t['tp1']=999999
        except Exception as e:
            print(e)
        time.sleep(60)

# Flask for Render Web Service port binding
app = Flask(__name__)
@app.route("/")
def home():
    return "LIVE BOT RUNNING 24/7"

# Start bot in background thread when gunicorn loads
threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    bot_loop()
