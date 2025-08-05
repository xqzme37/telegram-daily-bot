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
    # сохраняем chat_id в context.bot_data, чтобы потом слать туда
    context.application.bot_data["chat_id"] = update.effective_chat.id
    await update.message.reply_text("Привет! Я буду присылать тебе ежедневные вопросы.")

async def send_daily_questions(app):
    chat_id = app.bot_data.get("chat_id")
    if chat_id:
        await app.bot.send_message(chat_id=chat_id, text="Ежедневный вопрос: Как дела?")
    else:
        logger.warning("Нет сохранённого chat_id для отправки.")

async def main():
    application = Application.builder().token(TOKEN).build()

    # /start команда
    application.add_handler(CommandHandler("start", start))

    # Планировщик
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)
    scheduler.add_job(lambda: asyncio.create_task(send_daily_questions(application)),
                      "cron", hour=10, minute=0)
    scheduler.start()

    # Запуск бота вручную (без run_polling)
    await application.initialize()
    await application.start()
    logger.info("Бот запущен и ждёт события...")

    try:
        await asyncio.Event().wait()  # держим процесс живым
    finally:
        await application.stop()
        await application.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
