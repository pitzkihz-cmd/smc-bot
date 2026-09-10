from flask import Flask
import requests, threading, time
from datetime import datetime
import pytz

app = Flask(__name__)

BOT_TOKEN = "8967884674:AAEYIsjVIkMVZCdUU0P29EKvHMpY2guGKJs"
CHANNEL_ID = "@Smcpaviebotchannel"

data = {
  "XAUUSD": {"high": 0, "low": 99999, "history": [], "last_signal": 0},
  "EURUSD": {"high": 0, "low": 99999, "history": [], "last_signal": 0}
}

def send_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHANNEL_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        print(e)

def get_price(symbol):
    try:
        if symbol == "XAUUSD":
            r = requests.get("https://api.gold-api.com/price/XAU", timeout=10).json()
            return float(r.get("price", 0))
        else:
            r = requests.get("https://open.er-api.com/v6/latest/EUR", timeout=10).json()
            return float(r["rates"]["USD"])
    except:
        return 0

def get_session():
    utc = datetime.now(pytz.utc)
    hour = utc.hour
    # London 8-12 UTC, NY 13-17 UTC, Overlap 12-16 UTC is BEST
    if 8 <= hour <= 12: return "LONDON"
    if 13 <= hour <= 17: return "NEW YORK"
    if 12 <= hour <= 16: return "LONDON/NY OVERLAP 🔥 BEST"
    return "ASIA / LOW"

def is_a_plus_setup(symbol, price, side):
    d = data[symbol]
    history = d["history"]
    if len(history) < 20: return False, "Collecting data"

    # 1. Avoid spam - 1 signal per 30 min per pair max
    if time.time() - d["last_signal"] < 1800: return False, "Cooldown"

    # 2. Session filter - A+ only in London/NY
    session = get_session()
    if "ASIA" in session: return False, f"Bad session {session}"

    # 3. Liquidity sweep logic - price must have wicked past recent high/low then rejected
    recent_high = max(history[-20:])
    recent_low = min(history[-20:])

    if side == "BUY":
        # For BUY: must have swept low first (sell liquidity taken)
        swept = min(history[-10:]) < recent_low
        if not swept: return False, "No liquidity sweep"
    else:
        swept = max(history[-10:]) > recent_high
        if not swept: return False, "No liquidity sweep"

    # 4. Volatility filter
    volatility = max(history[-20:]) - min(history[-20:])
    if symbol == "XAUUSD" and volatility < 3: return False, "Choppy"
    if symbol == "EURUSD" and volatility < 0.0008: return False, "Choppy"

    return True, f"A+ Confluence | {session}"

def loop():
    send_telegram("✅ *A+ SMC BOT LIVE*\n\nPairs: XAUUSD + EURUSD\nFilter: BOS + Liquidity Sweep + Session (London/NY only)\nQuality: A+ Only = 1-3 signals/day but high accuracy\nMode: No Deriv, No TradingView")
    while True:
        for symbol in ["XAUUSD", "EURUSD"]:
            try:
                price = get_price(symbol)
                if price == 0: continue
                d = data[symbol]
                d["history"].append(price)
                if len(d["history"]) > 100: d["history"].pop(0)

                if len(d["history"]) < 20:
                    continue

                # BOS detection
                thresh = 2 if symbol == "XAUUSD" else 0.0005

                if price > d["high"] and d["high"]!= 0 and price - d["high"] > thresh:
                    ok, reason = is_a_plus_setup(symbol, price, "BUY")
                    if ok:
                        send_telegram(f"🔥 *A+ {symbol} BUY*\n\nEntry: {price}\nSL: {price - (8 if symbol=='XAUUSD' else 0.0010)}\nTP1: {price + (12 if symbol=='XAUUSD' else 0.0015)}\nTP2: {price + (25 if symbol=='XAUUSD' else 0.0030)}\n\n✅ BOS + Sweep + {reason}\nSession: {get_session()}\n\n*Only A+ setups - No gamble*")
                        d["last_signal"] = time.time()
                    d["high"] = price

                elif price < d["low"] and d["low"]!= 99999 and d["low"] - price > thresh:
                    ok, reason = is_a_plus_setup(symbol, price, "SELL")
                    if ok:
                        send_telegram(f"🔥 *A+ {symbol} SELL*\n\nEntry: {price}\nSL: {price + (8 if symbol=='XAUUSD' else 0.0010)}\nTP1: {price - (12 if symbol=='XAUUSD' else 0.0015)}\nTP2: {price - (25 if symbol=='XAUUSD' else 0.0030)}\n\n✅ BOS + Sweep + {reason}\nSession: {get_session()}\n\n*Only A+ setups - No gamble*")
                        d["last_signal"] = time.time()
                    d["low"] = price

                if price > d["high"]: d["high"] = price
                if price < d["low"]: d["low"] = price

            except Exception as e:
                print(e)
        time.sleep(20)

threading.Thread(target=loop, daemon=True).start()

@app.route('/')
def home(): return "A+ SMC LIVE - XAUUSD + EURUSD"

@app.route('/test')
def test():
    send_telegram(f"✅ *TEST OK - A+ MODE*\n\nPairs: XAUUSD + EURUSD\nSession now: {get_session()}\nFilter: Only best setups\nYour bot is ready - wait for London/NY session for A+ signal")
    return "A+ Test sent!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
