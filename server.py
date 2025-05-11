from flask import Flask, request
import requests
import os

app = Flask(__name__)

HELIUS_API_KEY = "dbef4b36-c729-48f8-bc51-dfc9387a97a8"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_deployer_via_helius(token_address):
    try:
        url = f"https://mainnet.helius.xyz/v0/addresses/{token_address}/transactions?api-key={HELIUS_API_KEY}&limit=10"
        res = requests.get(url)
        res.raise_for_status()
        txs = res.json()
        if not txs or not isinstance(txs, list):
            return None
        tx = txs[-1]  # Earliest transaction (reverse order)
        deployer = tx.get("feePayer") or tx.get("signer") or None
        return deployer
    except Exception as e:
        print("Helius Error:", e)
        return None

def get_other_tokens_by_wallet(wallet_address):
    try:
        url = f"https://public-api.solscan.io/account/tokens?account={wallet_address}&limit=50"
        res = requests.get(url, headers={"accept": "application/json"})
        tokens = []
        if res.status_code == 200:
            for t in res.json():
                tokens.append(t.get("tokenAddress"))
        return tokens
    except Exception as e:
        print("Solscan Token Lookup Error:", e)
        return []

def send_telegram_message(message: str):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram Error:", e)

@app.route("/")
def home():
    return "Solana CA Checker (Helius v2) is running."

@app.route("/check")
def check():
    ca = request.args.get("ca")
    if not ca:
        return {"error": "Missing 'ca' parameter"}, 400

    deployer = get_deployer_via_helius(ca)
    if not deployer:
        send_telegram_message(f"⚠️ 無法透過 Helius 查詢 CA: {ca} 的部署者")
        return {"error": "Helius 無法找到初始化交易"}, 404

    tokens = get_other_tokens_by_wallet(deployer)
    msg = f"📡 <b>SOL鏈 CA 分析</b>\n\n📌 Token Mint: <code>{ca}</code>\n👨‍💻 創建者 (Deployer): <code>{deployer}</code>\n\n📦 他持有的其他Token：\n"
    for t in tokens:
        msg += f"- {t}\n"
    send_telegram_message(msg)
    return {"status": "ok", "deployer": deployer, "tokens": tokens}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
