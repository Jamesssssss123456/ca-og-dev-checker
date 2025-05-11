import os
import requests
from telegram.ext import Updater, CommandHandler

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
RENDER_CHECK_URL = "https://ca-og-dev-checker.onrender.com/check?ca="

def check(update, context):
    if len(context.args) == 0:
        update.message.reply_text("❌ 請輸入 CA 地址，例如：/check 38Pgz...pump")
        return
    ca = context.args[0]
    update.message.reply_text(f"🔍 正在查詢 CA: {ca}")
    try:
        res = requests.get(RENDER_CHECK_URL + ca)
        if res.status_code == 200:
            data = res.json()
            deployer = data.get("deployer", "未知")
            name = data.get("name", "未知")
            symbol = data.get("symbol", "未知")
            update.message.reply_text(
                f"📡 <b>查詢成功</b>\n📌 Token: <code>{ca}</code>\n🏷 名稱: <b>{name} ({symbol})</b>\n👨‍💻 Deployer: <code>{deployer}</code>",
                parse_mode="HTML"
            )
        else:
            update.message.reply_text("⚠️ 查詢失敗，CA 可能無效或 GMGN 無法讀取")
    except Exception as e:
        update.message.reply_text(f"❌ 發生錯誤：{e}")

def start(update, context):
    update.message.reply_text("👋 歡迎使用 CA 查詢機器人！輸入 /check <ca> 即可查詢。")

def help_command(update, context):
    update.message.reply_text("/check <ca地址> - 查詢 CA 部署者與資訊")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("check", check))
    dp.add_handler(CommandHandler("help", help_command))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
