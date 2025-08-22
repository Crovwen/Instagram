import logging
import asyncio
from telegram import Update, ForceReply
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from instagrapi import Client

logging.basicConfig(level=logging.INFO)

USERNAME, PASSWORD, TARGET = range(3)
user_data = {}

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لطفاً یوزرنیم اینستاگرامتو بفرست:")
    return USERNAME

# دریافت یوزرنیم
async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data['username'] = update.message.text
    await update.message.reply_text("پسوردتو بفرست:")
    return PASSWORD

# دریافت پسورد و تلاش برای ورود
async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data['password'] = update.message.text
    await update.message.reply_text("درحال ورود به اکانت...")
    
    cl = Client()
    try:
        cl.login(user_data['username'], user_data['password'])
        user_data['client'] = cl
        await update.message.reply_text("✅ ورود موفق بود!\nآیدی فرد مقابلتو (مثلاً: example_user) بفرست:")
        return TARGET
    except Exception as e:
        await update.message.reply_text(f"❌ ورود ناموفق بود:\n{e}")
        return ConversationHandler.END

# حذف پیام‌ها
async def get_target_and_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_username = update.message.text
    cl = user_data['client']

    try:
        user_id = cl.user_id_from_username(target_username)
        threads = cl.direct_threads()
        deleted = 0

        for thread in threads:
            if user_id in thread.users:
                messages = cl.direct_messages(thread.id, amount=20)
                for msg in messages:
                    if msg.user_id == cl.user_id:
                        try:
                            cl.direct_delete_messages(thread.id, [msg.id])
                            deleted += 1
                        except:
                            pass

        await update.message.reply_text(f"✅ {deleted} پیام ارسالی شما برای @{target_username} حذف شد.")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در حذف پیام‌ها:\n{e}")
    
    return ConversationHandler.END

# لغو عملیات
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⛔️ عملیات لغو شد.")
    return ConversationHandler.END

# اجرای اصلی
async def main():
    app = ApplicationBuilder().token("8385635455:AAGSwcS-fol43Sd2ogy6-5rXgn5cRmOJnT8").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
            TARGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_target_and_delete)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main()) 
