from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import asyncio
import os

TOKEN = "8385635455:AAFIxFy8Ax1XR9qbP0WJ8LmbEqEjKOYgEPw"
APP_URL = "https://instagram-bvt4.onrender.com"  # 🔁 آدرس سرویس رندر تو

# ساخت اپلیکیشن
app = Flask(__name__)
bot_app = None  # برای استفاده در endpoint

# فرمان /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ربات با موفقیت فعاله! ✅")

# مسیر Webhook
@app.route('/webhook', methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    asyncio.run(bot_app.process_update(update))
    return "ok", 200

async def setup_bot():
    global bot_app
    bot_app = ApplicationBuilder().token(TOKEN).build()

    # ثبت فرمان‌ها
    bot_app.add_handler(CommandHandler("start", start))

    # ست کردن Webhook
    await bot_app.bot.set_webhook(f"{APP_URL}/webhook")
    print(f"Webhook set to {APP_URL}/webhook")

    return bot_app

if __name__ == '__main__':
    # راه‌اندازی بات در بک‌گراند
    asyncio.run(setup_bot())
    # اجرای سرور Flask
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
