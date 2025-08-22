from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)
from instagrapi import Client
import os

USERNAME, PASSWORD, TARGET = range(3)
user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لطفاً یوزرنیم اینستاگرام خودتو بفرست 📱")
    return USERNAME

async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["username"] = update.message.text.strip()
    await update.message.reply_text("حالا پسوردتو بفرست 🔐")
    return PASSWORD

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text.strip()
    username = context.user_data["username"]

    cl = Client()
    try:
        cl.login(username, password)
        user_sessions[update.effective_user.id] = cl
        await update.message.reply_text("✅ ورود موفقیت‌آمیز بود!\nحالا آیدی اینستاگرام کسی که می‌خوای پیام‌هات رو از چتش پاک کنم بفرست:")
        return TARGET
    except Exception as e:
        print("Login Error:", e)
        await update.message.reply_text("❌ ورود ناموفق بود. لطفاً یوزرنیم یا پسورد رو بررسی کن و دوباره /start رو بزن.")
        return ConversationHandler.END

async def get_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_username = update.message.text.strip()
    cl = user_sessions.get(update.effective_user.id)

    try:
        user_id = cl.user_id_from_username(target_username)
        threads = cl.direct_threads()

        thread_id = None
        for thread in threads:
            if any(user.pk == user_id for user in thread.users):
                thread_id = thread.id
                break

        if not thread_id:
            await update.message.reply_text("❌ چت با این کاربر پیدا نشد. ممکنه هنوز بهش پیام ندادی.")
            return ConversationHandler.END

        messages = cl.direct_messages(thread_id, amount=100)
        deleted_count = 0
        for msg in messages:
            if msg.user_id == cl.user_id:
                try:
                    cl.direct_delete_messages(thread_id, [msg.id])
                    deleted_count += 1
                except Exception as e:
                    print(f"خطا در حذف پیام {msg.id}: {e}")
                    continue

        await update.message.reply_text(f"✅ عملیات انجام شد.\nتعداد پیام‌های حذف‌شده: {deleted_count}")
    except Exception as e:
        print("Delete Error:", e)
        await update.message.reply_text("⚠️ خطایی رخ داد. آیدی رو چک کن یا بعداً دوباره تلاش کن.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("گفتگو لغو شد ❌")
    return ConversationHandler.END

# ----------------------------
# ✅ اجرای Webhook صحیح:
# ----------------------------
if __name__ == '__main__':
    import asyncio

    TOKEN = os.getenv("BOT_TOKEN") or "8385635455:AAFIxFy8Ax1XR9qbP0WJ8LmbEqEjKOYgEPw"
    DOMAIN = os.getenv("DOMAIN") or "https://instagram-bvt4.onrender.com"

    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
            TARGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_target)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    async def main():
        await app.run_webhook(
            listen="0.0.0.0",
            port=int(os.environ.get("PORT", 10000)),
            webhook_path=f"/webhook/{TOKEN}",
            webhook_url=f"{DOMAIN}/webhook/{TOKEN}",
        )

    asyncio.run(main())
