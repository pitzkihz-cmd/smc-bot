import yfinance as yf, requests, os, time
from datetime import datetime
import pytz
import matplotlib
matplotlib.use('Agg')
import mplfinance as mpf

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
    requests.post(url, json={"chat_id": CHAT_ID, "text": text})

def send_entry(sym, cfg, df, f70, f79, f88, sl, tp1, tp3, price):
    plot_df = df.tail(80).copy()
    path = f"/tmp/{sym.replace('.','_')}.png"
    hlines = dict(hlines=[f70, f79, f88, sl], colors=['#ff9800','#00c853','#ff1744','#ff1744'], linestyle='--')
    mpf.plot(plot_df, type='candle', style='yahoo',
             title=f"{sym} LIVE BUY {price:.{cfg['dec']}f}",
             ylabel='Price', hlines=hlines, volume=False,
             savefig=dict(fname=path, dpi=150, bbox_inches='tight'))
    caption = f"""{cfg['emoji']} {sym} LIVE BUY ENTRY
{datetime.now(EAT).strftime('%H:%M EAT')} PRICE NOW {price:.{cfg['dec']}f}

E1 {f70:.{cfg['dec']}f} (70%)
E2 {f79:.{cfg['dec']}f} MAIN
E3 {f88:.{cfg['dec']}f}
SL {sl:.{cfg['dec']}f}
Live monitoring TP1 {tp1:.{cfg['dec']}f} TP3 {tp3:.{cfg['dec']}f}
"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    with open(path, 'rb') as ph:
        requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"photo": ph})

def get_data(cfg):
    df = yf.Ticker(cfg['yf']).history(period="1d", interval="5m")
    if df.empty: return None, None
    for c in ['Open','High','Low','Close']: df[c] += cfg['offset']
    return df['Close'].iloc[-1], df

active = {}
send_text("✅ LIVE BOT 24/7: GOLD/BTC/EURUSD | Real price | TP sent AFTER hit only")

while True:
    try:
        for sym, cfg in SYMBOLS.items():
            price, df = get_data(cfg)
            if price is None: continue

            # ALL SESSIONS - NO TIME FILTER

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
                    print(f"ENTRY {sym} {price}")
            else:
                # REAL LIVE CHECK - SEND ONLY AFTER HIT
                t = active[sym]
                # LIVE PRICE = price variable every 60 sec
                if price <= t['sl']:
                    send_text(f"❌ {sym} SL HIT REAL LIVE\nEntry {t['entry']:.{cfg['dec']}f} -> SL {t['sl']:.{cfg['dec']}f}\nPrice NOW {price:.{cfg['dec']}f} | {datetime.now(EAT).strftime('%H:%M')}")
                    del active[sym]
                elif price >= t['tp3']:
                    send_text(f"✅ {sym} TP3 HIT REAL LIVE WIN\nEntry {t['entry']:.{cfg['dec']}f} -> TP3 {t['tp3']:.{cfg['dec']}f}\nProfit +{t['tp3']-t['f79']:.{cfg['dec']}f}\nPrice NOW {price:.{cfg['dec']}f} | {datetime.now(EAT).strftime('%H:%M')}")
                    del active[sym]
                elif price >= t['tp1'] and t['tp1']!= 999999:
                    send_text(f"🔔 {sym} TP1 HIT REAL LIVE -> MOVE TO BE\nPrice NOW {price:.{cfg['dec']}f} hit {t['tp1']:.{cfg['dec']}f} | Entry {t['entry']:.{cfg['dec']}f}")
                    t['tp1'] = 999999 # mark BE done, don't send again

    except Exception as e:
        print(e)
    time.sleep(60) # LIVE every 60 sec
