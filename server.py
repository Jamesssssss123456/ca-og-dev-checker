from flask import Flask, request
import requests
import os
import re

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def fetch_gmgn_info(ca_address):
    try:
        url = f"https://gmgn.ai/sol/token/{ca_address}"
        headers = {"User-Agent": "Mozilla/5.0"}
        html = requests.get(url, headers=headers).text

        # Extract deployer address from HTML using pattern (may vary)
        deployer_match = re.search(r'"deployerAddress":"([A-Za-z0-9]{32,44})"', html)
        deployer = deployer_match.group(1) if deployer_match else "未知"

        # Extract token name
        name_match = re.search(r'"tokenName":"(.*?)"', html)
        name = name_match.group(1) if name_match else "未知"

        # Extract token symbol
        symbol_match = re.search(r'"tokenSymbol":"(.*?)"', html)
        symbol = symbol_match.group(1) if symbol_match else "未知"

        return {
            "name": name,
            "symbol": symbol,
            "deployer": deployer
        }
    except Exception as e:
        print("GMGN Error:", e)
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
    return "Solana CA Checker (GMGN version) is live."

@app.route("/check")
def check():
    ca = request.args.get("ca")
    if not ca:
        return {"error": "Missing 'ca' parameter"}, 400

    # Strip "pump" suffix
    if ca.endswith("pump"):
        ca = ca[:-4]

    info = fetch_gmgn_info(ca)
    if not info:
        send_telegram_message(f"❌ 無法從 GMGN 讀取 CA: {ca} 的資訊")
        return {"error": "無法從 GMGN 讀取資料"}, 500

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
