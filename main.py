import os
import asyncio
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, filters
)
from instagrapi import Client

TOKEN = os.getenv("8385635455:AAENIQLo1J3npQU-wn0E4l1-NG7NCJH0rJk")
WEBHOOK_DOMAIN = os.getenv("https://instagram-bvt4.onrender.com")  # مثل: https://your-app-name.onrender.com

cl = Client()
USER, PASS = range(2)
user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! با دستور /login لاگین کن به اینستاگرامت.")

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧑 لطفاً یوزرنیم اینستاگرام رو بفرست:")
    return USER

async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["username"] = update.message.text
    await update.message.reply_text("🔒 حالا رمز اینستاگرامت رو بفرست:")
    return PASS

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = context.user_data["username"]
    password = update.message.text

    try:
        cl.login(username, password)
        user_sessions[update.effective_user.id] = cl.get_settings()
        await update.message.reply_text("✅ لاگین موفق بود!")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در لاگین: {e}")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⛔️ عملیات لغو شد.")
    return ConversationHandler.END

def setup_handlers(app):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("login", login)],
        states={
            USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username)],
            PASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

async def main():
    app = Application.builder().token(TOKEN).build()
    setup_handlers(app)

    await app.bot.set_webhook(f"{WEBHOOK_DOMAIN}/webhook")
    await app.run_webhook(
        listen="0.0.0.0",
        port=8000,
        webhook_path="/webhook"
    )

if __name__ == "__main__":
    asyncio.run(main()) 
