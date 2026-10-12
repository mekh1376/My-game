import logging
import os
import requests
from flask import Flask, jsonify, render_template, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

# تنظیمات لاگینگ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# آدرس دقیق مینی‌اپ روی رندر و گوگل اسکریپت
WEB_APP_URL = "https://my-telegrambot-8vwc.onrender.com"
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwMDIVf6-cRwYa5oQrggAo4AAzll_TVYvohpeQ45o6QHQtEy9Stm6ScE7JaGkj7CpPMxw/exec"
CHANNEL_URL = "https://t.me/LuckiyiybotChannel"
SUPPORT_URL = "https://t.me/luckiy_support"
BOT_USERNAME = "LuckiyiyBot"
TOKEN = os.environ.get("BOT_TOKEN")

RULES_TEXT = """📜 **راهنما و قوانین بازی گردونه**

✨ **به دنیای هیجان و جایزه خوش آمدید!**

1️⃣ **شانس‌های اولیه و روزانه:**
در شروع بازی، **۵ شانس رایگان** به عنوان هدیه دریافت می‌کنید. علاوه بر این، هر ۲۴ ساعت یک‌بار، **۲ شانس رایگان جدید** به حساب شما اضافه می‌شود تا همیشه شانس برنده شدن داشته باشید!

2️⃣ **دعوت از دوستان (شانس بی‌نهایت):**
می‌خواهید بیشتر بچرخانید؟ با ارسال لینک اختصاصی خود به دوستانتان، به ازای هر ورود، **شانس چرخش اضافه و سکه رایگان** هدیه بگیرید. این سریع‌ترین راه برای بالا کشیدن خودتان در جدول رقابت است!

3️⃣ **بخش ویژه شانس‌خانه (خرید شانس):**
اگر در یک قدمی رتبه‌های برتر هستید و شانس‌های رایگانتان تمام شده، می‌توانید از بخش فروشگاه/خرید، بسته‌های دلخواه شانس را تهیه کنید تا مسیر رسیدن به صدر جدول و جوایز بزرگ را شتاب ببخشید!

4️⃣ **جمع‌آوری سکه و جوایز ۳ نفر برتر:**
با هر چرخش، سکه جمع کنید. در پایان هر دوره، **۳ نفر اول جدول رده‌بندی** جوایز ویژه را از آن خود می‌کنند! همچنین سکه‌ها شانس شما را در قرعه‌کشی‌های بزرگ دوره‌ای بالا می‌برند.

5️⃣ **سلامت رقابت و قوانین:**
برای حفظ عدالت، استفاده از چند اکانت (مولتی‌اکانت)، اکانت‌های فیک یا ربات‌های تقلب اکیداً ممنوع است. در صورت مشاهده، تمامی سکه‌ها و حساب کاربر متخلف مسدود خواهد شد."""

# --- راه‌اندازی اپلیکیشن Flask ---
app = Flask(__name__, template_folder=".")

# راه‌اندازی ربات تلگرام
telegram_app = None
if TOKEN:
    telegram_app = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = f"TG_{user.id}"
    first_name = user.first_name or "دوست"
    last_name = user.last_name or ""
    full_name = f"{first_name} {last_name}".strip()
    username = f"@{user.username}" if user.username else "Guest"

    if context.args:
        arg = context.args[0]
        inviter_id = None
        if arg.startswith("ref_"):
            inviter_id = arg.replace("ref_", "")
        elif arg.startswith("TG_"):
            inviter_id = arg

        if inviter_id and inviter_id != user_id:
            try:
                requests.get(
                    f"{GOOGLE_SCRIPT_URL}?action=addSpins&userId={inviter_id}&count=2",
                    timeout=5,
                )
            except Exception as e:
                logging.error(f"Error adding referral spins: {e}")

    try:
        requests.get(
            f"{GOOGLE_SCRIPT_URL}?action=saveData&userId={user_id}&name={requests.utils.quote(full_name)}&username={requests.utils.quote(username)}&coins=0&spins=5&targetTime=0",
            timeout=5,
        )
    except Exception as e:
        logging.error(f"Error registering user on start: {e}")

    keyboard = [
        [InlineKeyboardButton("🎡 گردونه شانس", web_app=WebAppInfo(url=WEB_APP_URL))],
        [InlineKeyboardButton("👥 دعوت از دوستان", callback_data="invite_friends"), InlineKeyboardButton("📢 کانال ما", url=CHANNEL_URL)],
        [InlineKeyboardButton("📜 راهنما و قوانین", callback_data="show_rules"), InlineKeyboardButton("💬 پشتیبانی", url=SUPPORT_URL)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = f"سلام {first_name} عزیز! 🌶 به گردونه شانس طلایی خوش آمدید.\nاز دکمه زیر برای ورود به مینی‌اپ استفاده کن:"
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "show_rules":
        await query.message.reply_text(RULES_TEXT, parse_mode="Markdown")
    elif query.data == "invite_friends":
        referral_link = f"https://t.me/{BOT_USERNAME}?start=ref_TG_{user_id}"
        share_text = f"همین الان با این لینک وارد شو، گردونه رو بچرخون و سکه‌هاتو نقد کن! 🎯✨\n\n{referral_link}"
        share_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📲 اشتراک‌گذاری با دوستان", url=f"https://t.me/share/url?url={referral_link}&text={requests.utils.quote(share_text)}")]]))
        invite_msg = f"🎁 **لینک دعوت اختصاصی شما:**\n\n`{referral_link}`\n\nبا ارسال این لینک به دوستانت، به ازای هر ورود بلافاصله ۲ شانس چرخش هدیه بگیر! 🚀"
        await query.message.reply_text(invite_msg, parse_mode="Markdown", reply_markup=share_keyboard)

if telegram_app:
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CallbackQueryHandler(handle_callback))

@app.after_request
def add_header(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

@app.route("/")
def home():
    return render_template("index.html")

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    if telegram_app and request.method == "POST":
        update = Update.de_json(request.get_json(force=True), telegram_app.bot)
        telegram_app.update_queue.put(update)
    return "OK", 200

@app.route("/api/top-users", methods=["GET"])
def get_top_users():
    try:
        response = requests.get(f"{GOOGLE_SCRIPT_URL}?action=getLeaderboard", timeout=10)
        return jsonify({"status": "success", "top_users": response.json()})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/api/winners", methods=["GET"])
def get_winners():
    try:
        response = requests.get(f"{GOOGLE_SCRIPT_URL}?action=getWinnersHistory", timeout=10)
        return jsonify({"status": "success", "winners": response.json()})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    if TOKEN and telegram_app:
        # ست کردن خودکار وب‌هوک برای اتصال تلگرام به سرور رندر
        webhook_url = f"{WEB_APP_URL}/{TOKEN}"
        requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}")
        
        import asyncio
        asyncio.get_event_loop().run_until_complete(telegram_app.initialize())

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
