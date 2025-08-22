import logging
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from instagrapi import Client

# فعال‌سازی لاگ
logging.basicConfig(level=logging.INFO)

# متغیرها
user_sessions = {}  # user_id => {'username': ..., 'password': ...}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لطفا یوزرنیم اینستاگرامت رو بفرست.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in user_sessions:
        user_sessions[user_id] = {"username": text}
        await update.message.reply_text("پسوردت رو بفرست.")
    elif "password" not in user_sessions[user_id]:
        user_sessions[user_id]["password"] = text

        await update.message.reply_text("در حال ورود به حساب...")
        username = user_sessions[user_id]["username"]
        password = user_sessions[user_id]["password"]

        cl = Client()
        try:
            cl.login(username, password)
            await update.message.reply_text("✅ ورود موفقیت‌آمیز بود.")
            # اینجا می‌تونی بقیه عملیات رو انجام بدی
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در ورود: {e}")
            del user_sessions[user_id]
    else:
        await update.message.reply_text("شما قبلا لاگین کردی.")

async def main():
    app = ApplicationBuilder().token("8385635455:AAGSwcS-fol43Sd2ogy6-5rXgn5cRmOJnT8").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main()) 
