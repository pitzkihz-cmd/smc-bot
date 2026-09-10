from flask import Flask
import threading, time, requests, pytz
from datetime import datetime
import yfinance as yf
import pandas as pd

BOT_TOKEN = "8967884674:AAEYIsjVIkMVZCdUU0P29EKvHMpY2guGKJs"
CHAT_ID = "7804217051"
CHANNEL_ID = "7804217051"

app = Flask(__name__)

@app.route('/')
def home():
    return "GOLD BOT LIVE - SMC FULL PACKAGE ACTIVE"

@app.route('/test')
def test():
    r = send_telegram("✅ TEST OK - SMC Full Package Ready")
    return f"Sent: {r}"

def send_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
        return r.text
    except Exception as e:
        return str(e)

def get_price():
    try:
        df = yf.download("GC=F", period="1d", interval="1m", progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return float(df['Close'].iloc[-1])
    except:
        return None

def bot_loop():
    active = None
    last_sent = {}
    wins = 0
    losses = 0
    time.sleep(5)
    send_telegram("🚀 *GOLD SMC BOT ONLINE*\nFull Package Activated\nNY Session + Silver Bullet + BE + W/L\n@Smcpaviebot")

    while True:
        try:
            tz = pytz.timezone("Africa/Nairobi")
            now = datetime.now(tz)
            h = now.hour + now.minute/60.0

            # Track active trade
            if active is not None:
                price = get_price()
                if price is None:
                    time.sleep(10)
                    continue
                side = active["side"]
                if active.get("be_done") is False:
                    if (side == "SELL" and price <= active["tp1"]) or (side == "BUY" and price >= active["tp1"]):
                        send_telegram(f"🔔 *BE ALERT - {side}*\nTP1 `{active['tp1']:.1f}` hit!\nMove SL to BE!\nPrice now {price:.1f}")
                        active["be_done"] = True

                hit_tp3 = (price <= active["tp3"]) if side == "SELL" else (price >= active["tp3"])
                hit_sl = (price >= active["sl"]) if side == "SELL" else (price <= active["sl"])

                if hit_tp3:
                    wins += 1
                    send_telegram(f"✅ *WIN TP3 HIT +{abs(active['tp3']-active['e2']):.1f}$*\n{side} {active['strat']}\nScore {wins}W-{losses}L")
                    active = None
                elif hit_sl:
                    losses += 1
                    send_telegram(f"❌ *LOSS - SL HIT*\n{side} {active['strat']}\nScore {wins}W-{losses}L")
                    active = None
                time.sleep(15)
                continue

            # Only trade NY 10:00 - 23:30 EAT
            if not (10 <= h <= 23.5):
                time.sleep(60)
                continue

            df15 = yf.download("GC=F", period="5d", interval="15m", progress=False, auto_adjust=True)
            df5 = yf.download("GC=F", period="5d", interval="5m", progress=False, auto_adjust=True)
            if isinstance(df15.columns, pd.MultiIndex):
                df15.columns = df15.columns.get_level_values(0)
            if isinstance(df5.columns, pd.MultiIndex):
                df5.columns = df5.columns.get_level_values(0)
            df15 = df15.dropna()
            df5 = df5.dropna()
            if len(df15) < 30 or len(df5) < 30:
                time.sleep(30)
                continue

            spread = df5['High'].iloc[-1] - df5['Low'].iloc[-1]
            if spread > 10:
                time.sleep(30)
                continue

            rh = df15['High'].iloc[-20:-1].max()
            rl = df15['Low'].iloc[-20:-1].min()
            c15 = df15.iloc[-1]
            p15 = df15.iloc[-2]

            signal = None
            # BOS + Sweep
            if c15['Close'] > rh and p15['Close'] < rh and df5['Low'].iloc[-1] > df5['High'].iloc[-3]:
                signal = ("BUY", "BOS+Sweep", rl, rh)
            if c15['Close'] < rl and p15['Close'] > rl and df5['High'].iloc[-1] < df5['Low'].iloc[-3]:
                signal = ("SELL", "BOS+Sweep", rh, rl)
            # Silver Bullet 15:30-17:30 EAT
            if signal is None and 15.5 <= h <= 17.5:
                if df5['Low'].iloc[-1] > df5['High'].iloc[-3]:
                    signal = ("BUY", "Silver Bullet", df5['Low'].iloc[-1], rh)
                if df5['High'].iloc[-1] < df5['Low'].iloc[-3]:
                    signal = ("SELL", "Silver Bullet", df5['High'].iloc[-1], rl)

            if signal is None:
                time.sleep(20)
                continue

            side, strat, sweep, bos = signal
            key = f"{side}-{int(sweep)}"
            if key in last_sent and time.time() - last_sent[key] < 900:
                time.sleep(20)
                continue

            rng = abs(bos - sweep)
            if rng < 1:
                time.sleep(20)
                continue

            if side == "BUY":
                e2 = sweep + rng * 0.62
                sl = sweep - 0.5
                tp1 = sweep + rng * 0.9
                tp3 = bos + rng * 1.8
                e1 = sweep + rng * 0.5
                e3 = sweep + rng * 0.79
            else:
                e2 = sweep - rng * 0.62
                sl = sweep + 0.5
                tp1 = sweep - rng * 0.9
                tp3 = bos - rng * 1.8
                e1 = sweep - rng * 0.5
                e3 = sweep - rng * 0.79

            msg = f"🔥 *GOLD {side} | {strat}*\n{now.strftime('%H:%M EAT')} | {wins}W-{losses}L\n📍 E1 `{e1:.1f}`\n📍 E2 `{e2:.1f}` MAIN\n📍 E3 `{e3:.1f}`\nSL `{sl:.1f}`\n🎯 TP1 `{tp1:.1f}` BE\n🎯 TP3 `{tp3:.1f}`"
            send_telegram(msg)
            active = {"side": side, "strat": strat, "e2": e2, "sl": sl, "tp1": tp1, "tp3": tp3, "be_done": False}
            last_sent[key] = time.time()
            time.sleep(90)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
