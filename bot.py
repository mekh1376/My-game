import logging
import os
import requests
from flask import Flask, jsonify, render_template, request, render_template_string
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

WEB_APP_URL = "https://my-telegrambot-8vwc.onrender.com"
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwMDIVf6-cRwYa5oQrggAo4AAzll_TVYvohpeQ45o6QHQtEy9Stm6ScE7JaGkj7CpPMxw/exec"
CHANNEL_URL = "https://t.me/LuckiyiybotChannel"
SUPPORT_URL = "https://t.me/luckiy_support"
BOT_USERNAME = "LuckiyiyBot"
TOKEN = os.environ.get("BOT_TOKEN")

RULES_TEXT = """📜 **راهنما و قوانین بازی گردونه**

✨ **به دنیای هیجان و جایزه خوش آمدید!**
5 شانس رایگان اولیه دارید و با دعوت دوستان شانس بیشتری می‌گیرید."""

app = Flask(__name__, template_folder=".")

telegram_app = None
if TOKEN:
    telegram_app = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = f"TG_{user.id}"
    first_name = user.first_name or "دوست"
    
    keyboard = [
        [InlineKeyboardButton("🎡 گردونه شانس", web_app=WebAppInfo(url=WEB_APP_URL))],
        [InlineKeyboardButton("👥 دعوت از دوستان", callback_data="invite_friends"), InlineKeyboardButton("📢 کانال ما", url=CHANNEL_URL)],
        [InlineKeyboardButton("📜 راهنما و قوانین", callback_data="show_rules"), InlineKeyboardButton("💬 پشتیبانی", url=SUPPORT_URL)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"سلام {first_name} عزیز! از دکمه زیر برای ورود به مینی‌اپ استفاده کن:", reply_markup=reply_markup)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "show_rules":
        await query.message.reply_text(RULES_TEXT, parse_mode="Markdown")
    elif query.data == "invite_friends":
        referral_link = f"https://t.me/{BOT_USERNAME}?start=ref_TG_{user_id}"
        share_text = f"با این لینک وارد شو و گردونه رو بچرخون! 🎯\n\n{referral_link}"
        share_url = f"https://t.me/share/url?url={referral_link}&text={requests.utils.quote(share_text)}"
        share_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📲 اشتراک‌گذاری", url=share_url)]])
        await query.message.reply_text(f"لینک دعوت شما:\n`{referral_link}`", parse_mode="Markdown", reply_markup=share_keyboard)

if telegram_app:
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CallbackQueryHandler(handle_callback))

@app.after_request
def add_header(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

@app.route("/")
def home():
    try:
        return render_template("index.html")
    except Exception as e:
        return f"Template Error: {str(e)} - Make sure index.html is in root folder."

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    if telegram_app and request.method == "POST":
        import asyncio
        update = Update.de_json(request.get_json(force=True), telegram_app.bot)
        async def process():
            async with telegram_app:
                await telegram_app.process_update(update)
        try:
            asyncio.run(process())
        except Exception as e:
            logging.error(e)
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
    if TOKEN:
        webhook_url = f"{WEB_APP_URL}/{TOKEN}"
        try:
            requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}")
        except Exception as e:
            print(e)

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
