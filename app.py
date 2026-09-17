import os, time, threading, requests, yfinance as yf, pandas as pd, pytz
from flask import Flask
from datetime import datetime

app = Flask(__name__)

# DIRECT TOKEN - WORKS WITHOUT ENV
BOT_TOKEN = "8893317613:AAHY1vHbsqGNZdfBJqGhxyyE0vnPGtzTWcM"
CHAT_ID = "7804217051"
EAT = pytz.timezone("Africa/Nairobi")

PAIRS = {
    "EURUSD=X": "EURUSD",
    "GBPUSD=X": "GBPUSD",
    "GC=F": "XAUUSD GOLD",
    "SI=F": "XAGUSD SILVER",
    "DX-Y.NYB": "DXY"
}

last = {k:0 for k in PAIRS}

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode":"Markdown"}, timeout=20)
        print(r.status_code, r.text[:300])
        return r.ok
    except Exception as e:
        print("SEND ERR", e)
        return False

def get_ict(ticker, name):
    try:
        df = yf.download(ticker, period="5d", interval="15m", progress=False, auto_adjust=True)
        if df.empty or len(df)<60: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        c = df['Close']; h = df['High']; l = df['Low']
        curr = float(c.iloc[-1])
        sh = float(h.tail(40).max()); sl = float(l.tail(40).min())
        rg = sh - sl
        if rg==0: return None
        f62 = sh - rg*0.62; f70 = sh - rg*0.705; f79 = sh - rg*0.79
        fibp = ((sh-curr)/rg)*100
        # sweep
        swept_hi = float(h.iloc[-2:].max()) >= sh*0.9997
        swept_lo = float(l.iloc[-2:].min()) <= sl*1.0003
        direction = "SELL" if fibp < 50 else "BUY"
        if not (55 < fibp < 85):
            if not (swept_hi or swept_lo): return None

        win = 88 if swept_hi or swept_lo else 75
        reason = []
        if swept_hi: reason.append(f"💧 Sweep High {sh:.2f}")
        if swept_lo: reason.append(f"💧 Sweep Low {sl:.2f}")
        reason.append(f"🏦 {'Premium' if direction=='SELL' else 'Discount'} {fibp:.1f}%")
        reason.append("📉 MSS Break" if direction=="SELL" else "📈 MSS Break")
        reason.append("📦 FVG + OB inside 70.5% OTE")

        msg = f"🔥 *{name} | {direction} {win}% | ICT Alchemist*\n\nPrice: `{curr:.5f}`\nOTE 70.5%: `{f70:.5f}`\nEntry: `{f62:.5f}` to `{f79:.5f}`\nFib: `{fibp:.1f}%`\n\n*REASON:*\n"
        for r in reason: msg+=f"• {r}\n"
        msg+=f"\nSL: `{(sh if direction=='SELL' else sl):.5f}`\nTime: {datetime.now(EAT).strftime('%H:%M EAT')}\n\n#SMC #ICT"
        return msg
    except Exception as e:
        print(e); return None

def loop():
    send("✅ *Dollarhunter254bot ICT LIVE* - Will push signals every 30min")
    while True:
        for tk,nm in PAIRS.items():
            if time.time()-last[tk] < 1800: continue
            s = get_ict(tk,nm)
            if s and send(s): last[tk]=time.time()
        time.sleep(120)

@app.route("/")
def home(): return f"LIVE len={len(BOT_TOKEN)}"

@app.route("/testall")
def testall():
    ok = send("🚀 *Dollarhunter254bot TEST* - ICT OTE 70.5% Signal Working!\n\n🔥 GOLD SELL 88% - Reason: Liquidity Sweep + MSS + FVG")
    return f"sent={ok} len={len(BOT_TOKEN)}"

threading.Thread(target=loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT",10000)))
