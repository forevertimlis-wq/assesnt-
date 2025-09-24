from flask import Flask, request, Response
import json

app = Flask(__name__)

@app.route('/api/index', methods=['POST'])
def webhook():
    # Просто получаем данные и выводим их в лог
    try:
        update_data = request.get_json(force=True)
        print("!!! ПОЛУЧЕН ЗАПРОС ОТ TELEGRAM:")
        print(json.dumps(update_data, indent=2))
    except Exception as e:
        print(f"!!! ПРОИЗОШЛА ОШИБКА: {e}")
    
    # Отвечаем Telegram, что все в порядке
    return Response('ok', status=200)
