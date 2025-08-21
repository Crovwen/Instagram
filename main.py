from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ConversationHandler,
    ContextTypes, filters
)
from instagrapi import Client

# مرحله‌ها برای گفتگو
USERNAME, PASSWORD, TARGET = range(3)

# شروع بات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 سلام! برای شروع لطفاً یوزرنیم اینستاگرامتو بفرست:")
    return USERNAME

# دریافت یوزرنیم
async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['username'] = update.message.text.strip()
    await update.message.reply_text("🔐 حالا پسوردتو بفرست:")
    return PASSWORD

# دریافت پسورد
async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['password'] = update.message.text.strip()
    await update.message.reply_text("🎯 آیدی اینستاگرام کسی که می‌خوای پیام‌هاتو از دایرکتش حذف کنی رو بفرست:")
    return TARGET

# دریافت آیدی تارگت و اجرای عملیات
async def get_target_and_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_username = update.message.text.strip()
    username = context.user_data['username']
    password = context.user_data['password']

    await update.message.reply_text("🔄 در حال ورود به حساب اینستاگرام...")
    cl = Client()

    try:
        cl.login(username, password)
    except Exception as e:
        await update.message.reply_text("❌ ورود به اکانت ناموفق بود. لطفاً اطلاعات ورودتو بررسی کن.")
        return ConversationHandler.END

    try:
        user_id = cl.user_id_from_username(target_username)
        thread = cl.direct_thread_by_participants([user_id])
        messages = cl.direct_messages(thread.id)

        deleted_count = 0
        for msg in messages:
            if msg.user_id == cl.user_id:
                cl.direct_delete_messages(thread.id, [msg.id])
                deleted_count += 1

        await update.message.reply_text(f"✅ عملیات انجام شد. تعداد {deleted_count} پیام حذف شد.")
    except Exception as e:
        await update.message.reply_text("⚠️ خطایی رخ داد حین حذف پیام‌ها. لطفاً آیدی رو درست وارد کن یا مجدد تلاش کن.")

    return ConversationHandler.END

# لغو عملیات
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ عملیات لغو شد.")
    return ConversationHandler.END

# ساخت اپلیکیشن
app = ApplicationBuilder().token("8385635455:AAFIxFy8Ax1XR9qbP0WJ8LmbEqEjKOYgEPw").build()

# تعریف گفتگو
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

if __name__ == "__main__":
    app.run_webhook(
        listen="0.0.0.0",
        port=10000,
        url_path="8385635455:AAFIxFy8Ax1XR9qbP0WJ8LmbEqEjKOYgEPw",
        webhook_url="https://instagram-bvt4.onrender.com/8385635455:AAFIxFy8Ax1XR9qbP0WJ8LmbEqEjKOYgEPw"
    ) 
