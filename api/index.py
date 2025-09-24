import os
import asyncio
import google.generativeai as genai
from flask import Flask, request, Response
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- Настройка ---
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Конфигурация Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Создание приложения python-telegram-bot
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# --- Логика бота ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    system_instruction = """
    Ты — персональный психолог-консультант. Твоя задача — поддерживать пользователя,
    проявлять эмпатию и помогать ему разобраться в своих чувствах.
    Говори мягко и спокойно. Не давай прямых советов или команд.
    Вместо этого задавай уточняющие вопросы, которые помогут пользователю
    самому найти решение. Например, "Что вы чувствовали в тот момент?"
    или "Как эта ситуация влияет на вас сейчас?".
    Твои ответы должны быть краткими и направлены на поддержку диалога.
    """
    
    # Создаем "чат" с Gemini
    chat = model.start_chat(history=[
        {'role': 'user', 'parts': [system_instruction]},
        {'role': 'model', 'parts': ["Здравствуйте. Я готов выслушать вас. Расскажите, что вас беспокоит?"]}
    ])

    try:
        # Отправляем сообщение пользователя в Gemini и получаем ответ
        response = await chat.send_message_async(user_text)
        # Отправляем ответ пользователю в Telegram
        await update.message.reply_text(response.text)
    except Exception as e:
        print(f"Ошибка при общении с Gemini или отправке сообщения: {e}")

# Добавляем обработчик сообщений
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- Код для запуска (точка входа для Vercel) ---
app = Flask(__name__)

@app.route('/api/index', methods=['POST'])
def webhook():
    # Получаем данные от Telegram
    update_data = request.get_json(force=True)
    update = Update.de_json(update_data, application.bot)
    
    # Запускаем обработку сообщения в асинхронном режиме
    asyncio.run(application.process_update(update))
    
    # Отвечаем Telegram, что все в порядке
    return Response('ok', status=200)
