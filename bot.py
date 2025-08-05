import logging
from telegram.ext import Application, CommandHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import time
import pytz
import asyncio

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
    await context.bot.send_message(chat_id=context.job.chat_id, text="Ежедневный вопрос: Как дела?")

async def main():
    application = Application.builder().token(TOKEN).build()

    # /start команда
    application.add_handler(CommandHandler("start", start))

    # Планировщик
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)
    # Пример: отправка каждый день в 10:00
    scheduler.add_job(
        lambda: application.create_task(
            send_daily_questions(
                type("obj", (object,), {"bot": application.bot, "job": type("j", (object,), {"chat_id": ЧАТ_ID})()})
            )
        ),
        "cron",
        hour=10,
        minute=0
    )
    scheduler.start()

    logger.info("Бот запущен")
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
