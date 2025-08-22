import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from instagrapi import Client

logging.basicConfig(level=logging.INFO)

cl = Client()
SESSIONS = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لطفاً یوزرنیم اینستاگرام خود را ارسال کن.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in SESSIONS:
        SESSIONS[user_id] = {"step": "username", "username": text}
        await update.message.reply_text("حالا پسوردت رو بفرست.")
    elif SESSIONS[user_id]["step"] == "username":
        SESSIONS[user_id]["username"] = text
        SESSIONS[user_id]["step"] = "password"
        await update.message.reply_text("حالا پسوردت رو بفرست.")
    elif SESSIONS[user_id]["step"] == "password":
        username = SESSIONS[user_id]["username"]
        password = text
        try:
            cl.login(username, password)
            SESSIONS[user_id]["logged_in"] = True
            await update.message.reply_text("وارد شدیم! آیدی کسی که باهاش چت داشتی رو بفرست.")
            SESSIONS[user_id]["step"] = "target"
        except Exception as e:
            await update.message.reply_text(f"ورود ناموفق ❌\n{e}")
            del SESSIONS[user_id]
    elif SESSIONS[user_id]["step"] == "target":
        target_username = text
        try:
            user_id_ig = cl.user_id_from_username(target_username)
            messages = cl.direct_messages(user_id_ig)
            for msg in messages:
                cl.direct_delete_messages([msg.id])
            await update.message.reply_text("✅ همه پیام‌ها پاک شدن.")
            del SESSIONS[user_id]
        except Exception as e:
            await update.message.reply_text(f"خطا در حذف پیام‌ها:\n{e}")
            del SESSIONS[user_id]

async def main():
    app = ApplicationBuilder().token("8385635455:AAGSwcS-fol43Sd2ogy6-5rXgn5cRmOJnT8").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 
import asyncio

async def main():
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await application.updater.idle()
    await application.stop()
    await application.shutdown()

asyncio.run(main())
