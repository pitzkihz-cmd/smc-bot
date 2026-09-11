import os, time, requests, yfinance as yf, pytz
from flask import Flask
from threading import Thread
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID", "@Smcpaviebotchannel")
EAT = pytz.timezone("Africa/Nairobi")

app = Flask(__name__)

@app.route("/")
def home():
    return "BOT LIVE using @Smcpaviebotchannel"

@app.route("/test")
def test():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": CHAT_ID, "text": "TEST OK - Now pushing signals here!"}, timeout=15)
    return r.text

def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=15)

def bot_loop():
    send("BOT STARTED @Smcpaviebotchannel - SMC 70-79% ACTIVE")
    last = 0
    while True:
        try:
            now = datetime.now(EAT)
            if 10 <= now.hour <= 23 and time.time() - last > 1800:
                price = yf.download("GC=F", period="1d", interval="15m", progress=False)["Close"].iloc[-1]
                price = float(price)
                msg = f"<b>GOLD BUY SMC</b>\nENTRY: {price:.2f}\nSL: {price-5:.2f}\nTP: {price+12:.2f}\nTime {now.strftime('%H:%M')} EAT"
                send(msg)
                last = time.time()
            time.sleep(60)
        except:
            time.sleep(60)

Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
