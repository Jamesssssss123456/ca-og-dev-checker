from flask import Flask, request
import requests
import os

app = Flask(__name__)
SOLSCAN_API_BASE = "https://public-api.solscan.io"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_deployer(token_address):
    headers = {"accept": "application/json"}
    tx_url = f"{SOLSCAN_API_BASE}/account/tokens?account={token_address}&limit=5"
    tx_res = requests.get(tx_url, headers=headers)
    if tx_res.status_code != 200:
        return None
    tx_list = tx_res.json()
    if len(tx_list) == 0:
        return None
    return tx_list[0].get("owner")

def find_other_tokens_by_owner(owner_address):
    headers = {"accept": "application/json"}
    search_url = f"{SOLSCAN_API_BASE}/account/tokens?account={owner_address}&limit=50"
    res = requests.get(search_url, headers=headers)
    tokens = []
    if res.status_code == 200:
        data = res.json()
        for entry in data:
            tokens.append(entry.get("tokenAddress"))
    return tokens

def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(url, data=payload)

@app.route("/")
def home():
    return "Solana CA Checker Bot is live."

@app.route("/check")
def check():
    ca = request.args.get("ca")
    if not ca:
        return {"error": "Missing 'ca' parameter"}, 400

    deployer = get_deployer(ca)
    if not deployer:
        send_telegram_message(f"❌ 無法查詢 CA: {ca} 的初始錢包")
        return {"error": "No deployer found"}, 404

    tokens = find_other_tokens_by_owner(deployer)
    msg = f"📡 <b>SOL鏈 CA 分析</b>\n\n📌 Token Mint: <code>{ca}</code>\n👨‍💻 初始持有人: <code>{deployer}</code>\n\n📦 他持有的其他Token：\n"
    for t in tokens:
        msg += f"- {t}\n"
    send_telegram_message(msg)
    return {"status": "ok", "deployer": deployer, "tokens": tokens}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
