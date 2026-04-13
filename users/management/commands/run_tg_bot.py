import requests
from django.core.management.base import BaseCommand
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "8619549033:AAHdQ9DjuSp3LL6SGJv4J6Ucg340EPWGqpQ"
API_URL = "http://127.0.0.1:8000/api/telegram/link/"

class Command(BaseCommand):
    help = "Run Telegram bot"

    def handle(self, *args, **kwargs):

        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user = update.effective_user
            args = context.args

            if not args:
                await update.message.reply_text(
                    "❗ Открой ссылку с сайта для привязки аккаунта"
                )
                return

            token = args[0]

            try:
                response = requests.post(API_URL, json={
                    "token": token,
                    "telegram_id": user.id
                })

                if response.status_code == 200:
                    await update.message.reply_text("✅ Telegram успешно привязан!")
                else:
                    await update.message.reply_text("❌ Токен недействителен или устарел.")

            except Exception:
                await update.message.reply_text("⚠️ Ошибка соединения с сервером")

        app = ApplicationBuilder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))

        self.stdout.write(self.style.SUCCESS("🤖 Бот запущен"))
        app.run_polling()