from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from instagrapi import Client
import asyncio
import os

ASK_USERNAME, ASK_PASSWORD, ASK_TARGET = range(3)
user_data_store = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📥 لطفاً یوزرنیم اینستاگرام خود را وارد کنید:")
    return ASK_USERNAME

async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data_store[update.effective_chat.id] = {'username': update.message.text}
    await update.message.reply_text("🔐 حالا پسورد اینستاگرام را وارد کنید:")
    return ASK_PASSWORD

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data_store[update.effective_chat.id]['password'] = update.message.text
    await update.message.reply_text("🎯 لطفاً یوزرنیم فردی را وارد کنید که می‌خواهید پیام‌هایتان به او حذف شوند:")
    return ASK_TARGET

async def get_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = user_data_store[update.effective_chat.id]
    target_username = update.message.text
    await update.message.reply_text("⏳ در حال ورود به حساب اینستاگرام...")

    cl = Client()
    try:
        cl.login(data['username'], data['password'])
    except Exception as e:
        await update.message.reply_text(f"❌ ورود ناموفق: {e}")
        return ConversationHandler.END

    try:
        target_user_id = cl.user_id_from_username(target_username)
        thread = cl.direct_threads(selected_user_ids=[target_user_id])[0]

        count = 0
        for msg in thread.messages:
            if msg.user_id == cl.user_id:
                cl.direct_delete_messages(thread.id, [msg.id])
                count += 1
                await asyncio.sleep(0.3)

        await update.message.reply_text(f"✅ {count} پیام شما به @{target_username} با موفقیت حذف شد.")

    except Exception as e:
        await update.message.reply_text(f"⚠️ خطا هنگام حذف پیام‌ها: {e}")

    return ConversationHandler.END

if __name__ == "__main__":
    TOKEN = os.getenv("8385635455:AAGHECG2ZQ2_o5J6v8Wfx84ZNntPuD8hPfk")

    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username)],
            ASK_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
            ASK_TARGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_target)],
        },
        fallbacks=[],
    )

    app.add_handler(conv_handler)
    print("🤖 Bot is running...")
    app.run_polling() 
