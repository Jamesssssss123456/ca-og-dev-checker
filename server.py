from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def fetch_from_gmgn(ca):
    try:
        gmgn_url = f"https://gmgn.ai/api/token/{ca}"
        res = requests.get(gmgn_url)
        if res.status_code != 200:
            return None
        data = res.json()
        return {
            "name": data.get("tokenName", "未知"),
            "symbol": data.get("tokenSymbol", "未知"),
            "deployer": data.get("deployerAddress", "未知")
        }
    except Exception as e:
        print("GMGN Error:", e)
        return None

def fetch_from_axiom(ca):
    try:
        url = f"https://axiom.trade/meme/{ca}"
        headers = {"User-Agent": "Mozilla/5.0"}
        html = requests.get(url, headers=headers).text

        name = "未知"
        deployer = "未知"

        if 'ogToken' in html:
            import json, re
            name_line = [line for line in html.splitlines() if 'ogToken' in line]
            if name_line:
                raw = re.search(r'"ogToken":({.*?})', name_line[0])
                if raw:
                    obj = json.loads(raw.group(1))
                    name = obj.get("name", "未知")
                    deployer = obj.get("creator", "未知")

        return {
            "name": name,
            "symbol": name,
            "deployer": deployer
        }
    except Exception as e:
        print("Axiom Error:", e)
        return None

def send_telegram_message(message: str):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram Send Error:", e)

@app.route("/")
def home():
    return "Solana CA Checker API (Safe for Render)"

@app.route("/check")
def check():
    ca = request.args.get("ca")
    if not ca:
        return {"error": "Missing 'ca' parameter"}, 400

    if ca.endswith("pump"):
        ca = ca[:-4]

    info = fetch_from_gmgn(ca)
    if not info or info["name"] == "未知":
        info = fetch_from_axiom(ca)

    if not info:
        send_telegram_message(f"❌ 查詢失敗：無法在 GMGN 或 Axiom 找到 CA {ca} 資訊")
        return {"error": "無法從 GMGN / Axiom 查詢資料"}, 500

    msg = f"📡 <b>CA 分析</b>\n\n📌 Token Mint: <code>{ca}</code>\n🏷 名稱: <b>{info['name']} ({info['symbol']})</b>\n👨‍💻 Deployer: <code>{info['deployer']}</code>"
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
