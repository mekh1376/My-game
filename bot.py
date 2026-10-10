import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# توکن ربات تلگرام خود را اینجا وارد کنید
TOKEN = "8805606726:AAGuhscLLpB_62z9WObavHagxIv7WEMH-F0"
# لینک Web App گوگل‌شیت شما
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxJYQAelHDP-SpLtDwIg1-Rmspr3-4Bn_aw0LhKYWrOVeauN9Z6j1mZ6xIihb__wtJsPw/exec"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args  # پارامترهای ارجاعی مثل start=TG_123456
    
    welcome_message = f"سلام {user.first_name} عزیز! به گردونه شانس طلایی خوش آمدی. 🎯\nاز دکمه زیر برای ورود به مینی‌اپ استفاده کن:"
    
    # بررسی اینکه آیا کاربر با لینک دعوت آمده است یا خیر
    if args and len(args) > 0:
        inviter_id = args[0]  # شناسه معرف (مثلاً TG_157240459)
        
        # کاربر نمی‌تواند خودش خودش را دعوت کند
        if inviter_id != f"TG_{user.id}":
            try:
                # ارسال درخواست به گوگل‌شیت برای اضافه کردن ۲ شانس به معرف
                payload = {
                    "action": "addSpins",
                    "userId": inviter_id,
                    "count": 2
                }
                response = requests.get(GOOGLE_SCRIPT_URL, params=payload)
                data = response.json()
                
                if data.get("status") == "success":
                    # ارسال پیام تبریک به دعوت‌کننده
                    try:
                        pure_inviter_id = inviter_id.replace("TG_", "")
                        await context.bot.send_message(
                            chat_id=int(pure_inviter_id),
                            text="🎉 تبریک! یک نفر با لینک اختصاصی شما وارد ربات شد و ۲ شانس جدید به حساب شما اضافه گردید. 🎁"
                        )
                    except Exception as e:
                        print(f"Could not notify inviter: {e}")
            except Exception as e:
                print(f"Error updating spins in sheet: {e}")

    await update.message.reply_text(welcome_message)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    # ثبت دستور استارت
    application.add_handler(CommandHandler("start", start))
    
    print("Bot is running...")
    application.run_polling()
