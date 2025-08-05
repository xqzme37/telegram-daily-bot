import logging
from telegram.ext import Application, CommandHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import time
import pytz

# === НАСТРОЙКИ ===
TOKEN = "ТВОЙ_ТОКЕН"  # вставь сюда токен бота
TIMEZONE = pytz.timezone("Europe/Moscow")

# === ЛОГИ ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# === ХЕНДЛЕРЫ КОМАНД ===
async def start(update, context):
    await update.message.reply_text("Привет! Я бот, который шлёт ежедневные вопросы.")

async def send_daily_questions(context):
    chat_id = context.job.chat_id
    await context.bot.send_message(chat_id=chat_id, text="Ежедневный вопрос: Как дела?")

# === ЗАПУСК ===
def main():
    application = Application.builder().token(TOKEN).build()

    # Команда /start
    application.add_handler(CommandHandler("start", start))

    # Планировщик
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)
    # Например, отправлять каждый день в 10:00 по Москве
    scheduler.add_job(send_daily_questions, "cron", hour=10, minute=0, args=[application])
    scheduler.start()

    logger.info("Бот запущен")
    application.run_polling()

if __name__ == "__main__":
    main()
