import logging
import pytz
import os
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# === ЛОГИРОВАНИЕ ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# === НАСТРОЙКИ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ ===
TOKEN = os.getenv("TOKEN")
USERS = list(map(int, os.getenv("USERS", "").split(",")))
SUMMARY_CHAT_ID = int(os.getenv("SUMMARY_CHAT_ID"))

MOSCOW_TZ = pytz.timezone("Europe/Moscow")

responses = {}
QUESTIONS = [
    "1️⃣ Что ты сделал вчера?",
    "2️⃣ Что планируешь сегодня?",
    "3️⃣ Есть ли блокеры?"
]

# === ФУНКЦИИ ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я буду задавать тебе вопросы для дэйли в 12:00 по МСК.")

async def send_daily_questions(context: ContextTypes.DEFAULT_TYPE):
    global responses
    responses = {user_id: {"step": 0, "answers": []} for user_id in USERS}
    for user_id in USERS:
        await context.bot.send_message(chat_id=user_id, text="🕛 Время дэйли! Отвечай на вопросы:")
        await context.bot.send_message(chat_id=user_id, text=QUESTIONS[0])

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in responses:
        return

    user_state = responses[user_id]
    user_state["answers"].append(update.message.text)
    user_state["step"] += 1

    if user_state["step"] < len(QUESTIONS):
        await update.message.reply_text(QUESTIONS[user_state["step"]])
    else:
        await update.message.reply_text("✅ Спасибо! Твои ответы учтены.")
        if all(len(u["answers"]) == len(QUESTIONS) for u in responses.values()):
            await send_summary(context)

async def send_summary(context: ContextTypes.DEFAULT_TYPE):
    text = f"📋 Сводка за {datetime.now(MOSCOW_TZ).strftime('%d.%m.%Y')}:\n\n"
    for user_id, data in responses.items():
        user_name = (await context.bot.get_chat(user_id)).full_name
        text += f"👤 {user_name}\n"
        for q, ans in zip(QUESTIONS, data["answers"]):
            text += f"{q}\n➡ {ans}\n"
        text += "\n"
    await context.bot.send_message(chat_id=SUMMARY_CHAT_ID, text=text)

# === ОСНОВНОЙ КОД ===
async def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))

    scheduler = AsyncIOScheduler(timezone=MOSCOW_TZ)
    scheduler.add_job(send_daily_questions, trigger="cron", hour=12, minute=0, args=[application])
    scheduler.start()

    logging.info("Бот запущен")
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())


