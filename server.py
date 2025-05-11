from flask import Flask, request
import requests
import os

app = Flask(__name__)

HELIUS_API_KEY = "dbef4b36-c729-48f8-bc51-dfc9387a97a8"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_deployer_via_helius(token_address):
    url = f"https://mainnet.helius.xyz/v0/addresses/{token_address}/transactions?api-key={HELIUS_API_KEY}&limit=10"
    res = requests.get(url)
    if res.status_code != 200:
        return None
    txs = res.json()
    if not txs:
        return None
    # Get the earliest transaction involving the token
    tx = txs[-1]  # The last in list is earliest due to reverse order
    signer = tx.get("signer", tx.get("accountData", [{}])[0].get("account", None))
    return signer or tx.get("feePayer")

def get_other_tokens_by_wallet(wallet_address):
    url = f"https://public-api.solscan.io/account/tokens?account={wallet_address}&limit=50"
    res = requests.get(url, headers={"accept": "application/json"})
    tokens = []
    if res.status_code == 200:
        for t in res.json():
            tokens.append(t.get("tokenAddress"))
    return tokens

def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(url, data=payload)

@app.route("/")
def home():
    return "Solana CA Checker (Helius version) is live."

@app.route("/check")
def check():
    ca = request.args.get("ca")
    if not ca:
        return {"error": "Missing 'ca' parameter"}, 400

    deployer = get_deployer_via_helius(ca)
    if not deployer:
        send_telegram_message(f"❌ 無法透過 Helius 查詢 CA: {ca} 的部署者")
        return {"error": "No deployer found via Helius"}, 404

    tokens = get_other_tokens_by_wallet(deployer)
    msg = f"📡 <b>SOL鏈 CA 分析</b>\n\n📌 Token Mint: <code>{ca}</code>\n👨‍💻 創建者 (Deployer): <code>{deployer}</code>\n\n📦 他持有的其他Token：\n"
    for t in tokens:
        msg += f"- {t}\n"
    send_telegram_message(msg)
    return {"status": "ok", "deployer": deployer, "tokens": tokens}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
