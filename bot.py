import logging
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    WebAppInfo,
)
from telegram.ext import Application, CommandHandler, ContextTypes

# تنظیمات لاگینگ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ثوابت و اطلاعات ربات
WEB_APP_URL = (
    "https://my-game-xxxx.onrender.com"  # آدرس مینی‌اپ خود را بررسی/جایگزین کنید
)
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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name or "دوست"

    # کیبورد اصلی شیشه‌ای (منو)
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
        f"سلام {first_name} عزیز! 🌶 به گردونه شانس طلایی خوش آمدی.\n"
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
        # ساخت لینک اختصاصی رفرال برای کاربر
        referral_link = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"
        share_text = f"همین الان گردونه رو بچرخون و سکه‌هاتو نقد کن! 🎯✨ چند تا شانس رایگان داری، از دستش نده ⚡️👇\n{referral_link}"

        # دکمه اشتراک‌گذاری مستقیم
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
            f"با ارسال این لینک به دوستانت، با هر ثبت‌نام شانس چرخش اضافه دریافت کن! 🚀"
        )

        await query.message.reply_text(
            invite_msg, parse_mode="Markdown", reply_markup=share_keyboard
        )


def main():
    import os

    TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

    application = Application.builder().token(TOKEN).build()

    from telegram.ext import CallbackQueryHandler

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback))

    application.run_polling()


if __name__ == "__main__":
    main()
