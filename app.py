from flask import Flask, request
import requests
app = Flask(__name__)
BOT_TOKEN = "8967884674:AAEYIsjVIkMVZCdUU0P29EKvHMpY2guGKJs"
CHANNEL_ID = "@Smcpaviebotchannel"
def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id":CHANNEL_ID,"text":text,"parse_mode":"Markdown"})
@app.route('/webhook', methods=['POST'])
def webhook():
    d=request.get_json(force=True)
    price=float(d.get('price',0)); sl=float(d.get('sl',0))
    if price==0: return "OK",200
    risk=abs(price-sl); action=d.get('action','BUY')
    tp=price+risk*2.5 if action=="BUY" else price-risk*2.5
    msg=f"🔔 *{action} {d.get('symbol','EURUSD')}*\nEntry: `{price}`\nSL: `{sl}`\nTP: `{tp}`\n\n@Smcpaviebotchannel"
    send_telegram(msg)
    return "OK",200
@app.route('/test')
def test():
    send_telegram("✅ *SMC Bot is LIVE!* Connected to @Smcpaviebotchannel")
    return "Test Sent! Check Telegram"
@app.route('/')
def home():
    return "Bot Running"
