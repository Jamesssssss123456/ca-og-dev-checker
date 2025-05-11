from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def fetch_gmgn_info_from_api(ca_address):
    try:
        api_url = f"https://gmgn.ai/api/token/{ca_address}"
        res = requests.get(api_url)
        if res.status_code != 200:
            return None
        data = res.json()
        name = data.get("tokenName", "未知")
        symbol = data.get("tokenSymbol", "未知")
        deployer = data.get("deployerAddress", "未知")
        return {
            "name": name,
            "symbol": symbol,
            "deployer": deployer
        }
    except Exception as e:
        print("GMGN API Error:", e)
        return None

def send_telegram_message(message: str):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram Error:", e)

@app.route("/")
def home():
    return "Solana CA Checker (GMGN API version) is online."

@app.route("/check")
def check():
    ca = request.args.get("ca")
    if not ca:
        return {"error": "Missing 'ca' parameter"}, 400

    if ca.endswith("pump"):
        ca = ca[:-4]

    info = fetch_gmgn_info_from_api(ca)
    if not info:
        send_telegram_message(f"❌ 無法從 GMGN API 查詢 CA: {ca}")
        return {"error": "無法從 GMGN API 查詢資料"}, 500

    msg = f"📡 <b>pum.fun CA 分析</b>\n\n📌 Token Mint: <code>{ca}</code>\n🏷 名稱: <b>{info['name']} ({info['symbol']})</b>\n👨‍💻 Deployer: <code>{info['deployer']}</code>"
    send_telegram_message(msg)

    return {
        "status": "ok",
        "ca": ca,
        "name": info['name'],
        "symbol": info['symbol'],
        "deployer": info['deployer']
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
