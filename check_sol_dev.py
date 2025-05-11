import requests
import sys

SOLSCAN_API_BASE = "https://public-api.solscan.io"

def get_deployer(token_address):
    headers = {
        "accept": "application/json"
    }
    # Get token info
    token_info_url = f"{SOLSCAN_API_BASE}/token/meta?tokenAddress={token_address}"
    res = requests.get(token_info_url, headers=headers)
    if res.status_code != 200:
        return None
    token_data = res.json()
    
    # Get token creation/initialize transaction info
    tx_url = f"{SOLSCAN_API_BASE}/account/tokens?account={token_address}&limit=5"
    tx_res = requests.get(tx_url, headers=headers)
    if tx_res.status_code != 200:
        return None
    tx_list = tx_res.json()
    if len(tx_list) == 0:
        return None
    owner = tx_list[0].get("owner")
    return owner

def find_other_tokens_by_owner(owner_address):
    headers = {
        "accept": "application/json"
    }
    search_url = f"{SOLSCAN_API_BASE}/account/tokens?account={owner_address}&limit=50"
    res = requests.get(search_url, headers=headers)
    tokens = []
    if res.status_code == 200:
        data = res.json()
        for entry in data:
            tokens.append(entry.get("tokenAddress"))
    return tokens

def send_telegram_message(message: str):
    TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
    CHAT_ID = 'YOUR_CHAT_ID'
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(url, data=payload)

if __name__ == "__main__":
    ca = sys.argv[1]
    deployer = get_deployer(ca)
    if deployer:
        tokens = find_other_tokens_by_owner(deployer)
        msg = f"📡 <b>SOL鏈 CA 分析</b>\n\n📌 Token Mint: <code>{ca}</code>\n👨‍💻 初始持有人: <code>{deployer}</code>\n\n📦 他持有的其他Token：\n"
        for t in tokens:
            msg += f"- {t}\n"
        send_telegram_message(msg)
    else:
        send_telegram_message(f"❌ 無法查詢 CA: {ca} 的初始錢包")
