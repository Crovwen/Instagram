import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from instagrapi import Client

# مراحل گفتگو
ASK_USERNAME, ASK_PASSWORD, ASK_TARGET = range(3)

# ذخیره اطلاعات کاربران
user_sessions = {}

# لاگ‌گیری
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# شروع بات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 سلام! لطفاً یوزرنیم اینستاگرامت رو بفرست:")
    return ASK_USERNAME

# دریافت یوزرنیم
async def ask_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_sessions[user_id] = {"username": update.message.text}
    await update.message.reply_text("✅ حالا پسورد اینستاگرامت رو بفرست:")
    return ASK_PASSWORD

# دریافت پسورد
async def ask_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_sessions[user_id]["password"] = update.message.text
    await update.message.reply_text("🔍 حالا آیدی اینستاگرام فردی که می‌خوای پیام‌ها رو حذف کنی بفرست:")
    return ASK_TARGET

# دریافت آیدی هدف و حذف پیام‌ها
async def ask_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    session = user_sessions.get(user_id)

    if not session:
        await update.message.reply_text("❌ خطا: لطفاً دوباره `/start` رو بزن.")
        return ConversationHandler.END

    target_username = update.message.text

    try:
        cl = Client()
        cl.login(session["username"], session["password"])

        user_id_target = cl.user_id_from_username(target_username)
        threads = cl.direct_threads()

        deleted = 0

        for thread in threads:
            if thread.users[0].pk == user_id_target:
                for message in thread.messages:
                    if message.user_id == cl.user_id:
                        try:
                            cl.direct_delete_messages(thread.id, [message.id])
                            deleted += 1
                        except:
                            continue

        await update.message.reply_text(f"✅ {deleted} پیام حذف شد.")

    except Exception as e:
        await update.message.reply_text(f"⚠️ خطا در ورود یا حذف پیام‌ها:\n{e}")

    return ConversationHandler.END

# کنسل کردن مکالمه
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⛔️ عملیات لغو شد.")
    return ConversationHandler.END

# اجرای اصلی
if __name__ == '__main__':
    import asyncio

    async def main():
        app = ApplicationBuilder().token("8385635455:AAGSwcS-fol43Sd2ogy6-5rXgn5cRmOJnT8").build()

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={
                ASK_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_username)],
                ASK_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_password)],
                ASK_TARGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_target)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )

        app.add_handler(conv_handler)

        print("Bot is running...")
        await app.run_polling()

    asyncio.run(main())
