from flask import Flask, request
import requests, os, threading, time

app = Flask(__name__)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHANNEL_ID = os.environ.get("TELEGRAM_CHAT_ID", "@Smcpaviebotchannel")

last_high = 0
last_low = 99999

def send_telegram(text):
    if not BOT_TOKEN: return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHANNEL_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        print(e)

def get_gold_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=10).json()
        return float(r.get("price", 0))
    except:
        return 0

def free_smc_loop():
    global last_high, last_low
    send_telegram("✅ *FREE SMC BOT LIVE*\n\nPair: XAUUSD\nTF: 5m\nMode: SIGNALS ONLY\nBot watching Gold now...")
    while True:
        try:
            price = get_gold_price()
            if price == 0:
                time.sleep(15)
                continue
            if price > last_high and last_high != 0:
                if price - last_high > 2:
                    send_telegram(f"🔔 *XAUUSD BUY - BOS*\n\nEntry: {price:.2f}\nSL: {price-8:.2f}\nTP: {price+20:.2f}")
                    last_high = price
            elif price < last_low and last_low != 99999:
                if last_low - price > 2:
                    send_telegram(f"🔔 *XAUUSD SELL - BOS*\n\nEntry: {price:.2f}\nSL: {price+8:.2f}\nTP: {price-20:.2f}")
                    last_low = price
            if price > last_high: last_high = price
            if price < last_low: last_low = price
            time.sleep(20)
        except:
            time.sleep(20)

threading.Thread(target=free_smc_loop, daemon=True).start()

@app.route('/')
def home(): return "FREE SMC Signals Only"

@app.route('/test')
def test():
    send_telegram("✅ *TEST OK - Signals Working!*")
    return "Test sent!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
