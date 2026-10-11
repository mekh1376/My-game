import logging
import os
import requests
from threading import Thread
from flask import Flask, jsonify, render_template
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

# تنظیمات لاگینگ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# آدرس مینی‌اپ روی رندر و گوگل اسکریپت جدید
WEB_APP_URL = "https://my-telegrambot-8vwc.onrender.com"
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwY9iiHV_ohus1l229UnCWHzvjHGQLGZsRESlOGGpejORDD9rBJ5P2hOb9Cew0Kk6vzSg/exec"
CHANNEL_URL = "https://t.me/LuckiyiybotChannel"
SUPPORT_URL = "https://t.me/luckiy_support"
BOT_USERNAME = "LuckiyiyBot"

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

# --- بخش وب‌سرور Flask ---
app = Flask(__name__, template_folder=".")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/top-users", methods=["GET"])
def get_top_users():
    try:
        response = requests.get(f"{GOOGLE_SCRIPT_URL}?action=getLeaderboard", timeout=10)
        data = response.json()
        return jsonify({"status": "success", "top_users": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/api/winners", methods=["GET"])
def get_winners():
    try:
        response = requests.get(f"{GOOGLE_SCRIPT_URL}?action=getWinnersHistory", timeout=10)
        data = response.json()
        return jsonify({"status": "success", "winners": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


# --- بخش ربات تلگرام ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = f"TG_{user.id}"
    first_name = user.first_name or "دوست"
    last_name = user.last_name or ""
    full_name = f"{first_name} {last_name}".strip()
    username = f"@{user.username}" if user.username else "Guest"

    # بررسی لینک دعوت
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
            f"{GOOGLE_SCRIPT_URL}?action=saveData&userId={user_id}&name={requests.utils.quote(full_name)}&username={requests.utils.quote(username)}&coins=0&spins=5",
            timeout=5,
        )
    except Exception as e:
        logging.error(f"Error registering user on start: {e}")

    keyboard = [
        [
            InlineKeyboardButton(
                "🎡 گردونه شانس", web_app=WebAppInfo(url=WEB_APP_URL)
            )
        ],
        [
            InlineKeyboardButton(
                "👥 دعوت از دوستان", callback_data="invite_friends"
            ),
            InlineKeyboardButton("📢 کانال ما", url=CHANNEL_URL),
        ],
        [
            InlineKeyboardButton(
                "📜 راهنما و قوانین", callback_data="show_rules"
            ),
            InlineKeyboardButton("💬 پشتیبانی", url=SUPPORT_URL),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        f"سلام {first_name} عزیز! 🌶 به گردونه شانس طلایی خوش آمدید.\n"
        f"از دکمه زیر برای ورود به مینی‌اپ استفاده کن:"
    )

    await update.message.reply_text(welcome_text, reply_markup=reply_markup)


async def handle_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "show_rules":
        await query.message.reply_text(RULES_TEXT, parse_mode="Markdown")

    elif query.data == "invite_friends":
        referral_link = f"https://t.me/{BOT_USERNAME}?start=ref_TG_{user_id}"
        share_keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📲 اشتراک‌گذاری با دوستان",
                        url=f"https://t.me/share/url?url={referral_link}&text=همین%20الان%20گردونه%20رو%20بچرخون%20و%20سکه‌هاتو%20نقد%20کن!%20🎯✨%20چند%20تا%20شانس%20رایگان%20داری،%20از%20دستش%20نده%20⚡️",
                    )
                ]
            ]
        )

        invite_msg = (
            f"🎁 **لینک دعوت اختصاصی شما:**\n\n"
            f"`{referral_link}`\n\n"
            f"با ارسال این لینک به دوستانت، به ازای هر ورود بلافاصله ۲ شانس چرخش هدیه بگیر! 🚀"
        )

        await query.message.reply_text(
            invite_msg, parse_mode="Markdown", reply_markup=share_keyboard
        )


def main():
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        print("Error: BOT_TOKEN environment variable not set!")
        return

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback))

    web_thread = Thread(target=run_web)
    web_thread.daemon = True
    web_thread.start()

    print("Bot is running...")
    application.run_polling()


if __name__ == "__main__":
    main()
