from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from instagrapi import Client
import asyncio

sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome!\nSend your Instagram username:")

    sessions[update.effective_user.id] = {
        "step": "username"
    }

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text.strip()

    if user_id not in sessions:
        await update.message.reply_text("Please send /start first.")
        return

    session = sessions[user_id]

    if session["step"] == "username":
        session["username"] = message
        session["step"] = "password"
        await update.message.reply_text("🔐 Now send your Instagram password:")

    elif session["step"] == "password":
        session["password"] = message
        session["step"] = "target"
        await update.message.reply_text("👤 Send target Instagram username to delete your messages from chat:")

    elif session["step"] == "target":
        session["target"] = message
        await update.message.reply_text("🔄 Trying to login and delete your messages...")

        try:
            cl = Client()
            cl.login(session["username"], session["password"])

            user_id_target = cl.user_id_from_username(session["target"])
            thread = cl.direct_threads(user_ids=[user_id_target])[0]

            deleted = 0
            for msg in thread.messages:
                if msg.user_id == cl.user_id:
                    cl.direct_delete_messages(thread.id, [msg.id])
                    deleted += 1

            await update.message.reply_text(f"✅ Deleted {deleted} messages you sent to @{session['target']}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")

        del sessions[user_id]

app = ApplicationBuilder().Token("8385635455:AAFIxFy8Ax1XR9qbP0WJ8LmbEqEjKOYgEPw").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

app.run_polling() 
