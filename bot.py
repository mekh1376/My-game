import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='.')

WEB_APP_URL = "https://my-telegrambot-8vwc.onrender.com"
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwMDIVf6-cRwYa5oQrggAo4AAzll_TVYvohpeQ45o6QHQtEy9Stm6ScE7JaGkj7CpPMxw/exec"
TOKEN = os.environ.get("BOT_TOKEN")

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Error loading index.html: {str(e)}"

@app.route('/health')
def health():
    return "OK", 200

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    # دریافت پیام‌های تلگرام به صورت لایت و بدون درگیری پردازشی سنگین
    if request.method == 'POST':
        data = request.get_json(force=True)
        if 'message' in data:
            chat_id = data['message']['chat']['id']
            text = data['message'].get('text', '')
            if text.startswith('/start'):
                # ارسال پاسخ خوش‌آمدگویی ساده از طریق API تلگرام
                send_welcome(chat_id)
    return 'OK', 200

def send_welcome(chat_id):
    if not TOKEN:
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "سلام! به گردونه شانس خوش آمدید. از دکمه زیر برای باز کردن مینی‌اپ استفاده کنید:",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "🎡 گردونه شانس", "web_app": {"url": WEB_APP_URL}}]
            ]
        }
    }
    requests.post(url, json=payload)

@app.route('/api/top-users', methods=['GET'])
def get_top_users():
    try:
        response = requests.get(f"{GOOGLE_SCRIPT_URL}?action=getLeaderboard", timeout=10)
        return jsonify({"status": "success", "top_users": response.json()})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/winners', methods=['GET'])
def get_winners():
    try:
        response = requests.get(f"{GOOGLE_SCRIPT_URL}?action=getWinnersHistory", timeout=10)
        return jsonify({"status": "success", "winners": response.json()})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    # تنظیم خودکار وب‌هوک هنگام استارت
    if TOKEN:
        webhook_url = f"{WEB_APP_URL}/{TOKEN}"
        requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}")

    # خواندن دقیق پورت رندر
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
