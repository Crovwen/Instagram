import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from instagrapi import Client
import os

# لاگ برای دیباگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# وضعیت گفتگو
ASK_USERNAME, ASK_PASSWORD, ASK_TARGET = range(3)

# ذخیره سشن اینستاگرام
cl = Client()

# مسیر ذخیره سشن
SESSION_PATH = "session"

if not os.path.exists(SESSION_PATH):
    os.makedirs(SESSION_PATH)

# شروع
def start(update, context):
    update.message.reply_text("سلام! برای شروع، یوزرنیم اینستاگرامت رو بفرست:")
    return ASK_USERNAME

# دریافت یوزرنیم
def ask_username(update, context):
    context.user_data['insta_username'] = update.message.text
    update.message.reply_text("حالا پسورد اینستاگرامت رو بفرست:")
    return ASK_PASSWORD

# دریافت پسورد
def ask_password(update, context):
    context.user_data['insta_password'] = update.message.text
    update.message.reply_text("الان یوزرنیم کسی که می‌خوای چت‌هات باهاش پاک بشه رو بفرست:")
    return ASK_TARGET

# حذف پیام‌ها
def delete_messages(update, context):
    insta_user = context.user_data['insta_username']
    insta_pass = context.user_data['insta_password']
    target_username = update.message.text

    try:
        cl.load_settings(SESSION_PATH + f"/{insta_user}.json")
    except:
        pass

    try:
        cl.login(insta_user, insta_pass)
        cl.dump_settings(SESSION_PATH + f"/{insta_user}.json")
    except Exception as e:
        update.message.reply_text(f"❌ لاگین به اینستاگرام ناموفق بود:\n{e}")
        return ConversationHandler.END

    try:
        user_id = cl.user_id_from_username(target_username)
        threads = cl.direct_threads()
        deleted = 0
        for t in threads:
            if user_id in [u.pk for u in t.users]:
                for item in t.messages:
                    if item.user_id == cl.user_id:
                        cl.message_delete(item.id, thread_id=t.id)
                        deleted += 1
        update.message.reply_text(f"✅ {deleted} پیام با {target_username} حذف شد.")
    except Exception as e:
        update.message.reply_text(f"❌ خطا در حذف پیام‌ها:\n{e}")

    return ConversationHandler.END

# کنسل
def cancel(update, context):
    update.message.reply_text("⛔️ عملیات لغو شد.")
    return ConversationHandler.END

# اجرای اصلی
def main():
    TOKEN = "توکن ربات تلگرامت اینجا"

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_USERNAME: [MessageHandler(Filters.text & ~Filters.command, ask_username)],
            ASK_PASSWORD: [MessageHandler(Filters.text & ~Filters.command, ask_password)],
            ASK_TARGET: [MessageHandler(Filters.text & ~Filters.command, delete_messages)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
