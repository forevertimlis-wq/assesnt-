import os
import asyncio
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- Настройка ---
# Получаем ключи из переменных окружения (более безопасно)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Конфигурируем Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- Основная логика бота ---

# Эта функция будет вызываться на каждое сообщение от пользователя
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # Системная инструкция для Gemini: задаем роль психолога
    # Это самая важная часть! Здесь мы "настраиваем" нейросеть
    system_instruction = """
    Ты — персональный психолог-консультант. Твоя задача — поддерживать пользователя,
    проявлять эмпатию и помогать ему разобраться в своих чувствах.
    Говори мягко и спокойно. Не давай прямых советов или команд.
    Вместо этого задавай уточняющие вопросы, которые помогут пользователю
    самому найти решение. Например, "Что вы чувствовали в тот момент?"
    или "Как эта ситуация влияет на вас сейчас?".
    Твои ответы должны быть краткими и направлены на поддержку диалога.
    """

    # Создаем "чат" с Gemini, начиная с системной инструкции
    chat = model.start_chat(history=[
        {'role': 'user', 'parts': [system_instruction]},
        {'role': 'model', 'parts': ["Здравствуйте. Я готов выслушать вас. Расскажите, что вас беспокоит?"]}
    ])

    # Отправляем сообщение пользователя в Gemini и получаем ответ
    response = await chat.send_message_async(user_text)

    # Отправляем ответ от Gemini пользователю в Telegram
    await update.message.reply_text(response.text)


# --- Код для запуска (специфичен для Vercel) ---

# Создаем приложение
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
# Добавляем обработчик всех текстовых сообщений
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Эта асинхронная функция будет точкой входа для Vercel
async def main(request, response):
    await application.initialize()
    update = Update.de_json(await request.json(), application.bot)
    await application.process_update(update)
    return response.status(200).send("OK")