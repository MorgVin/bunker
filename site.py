from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import hashlib

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# 9 аватаров
AVATARS = [
    '/static/avatars/avatar1.jpg',
    '/static/avatars/avatar2.jpg',
    '/static/avatars/avatar3.jpg',
    '/static/avatars/avatar4.jpg',
    '/static/avatars/avatar5.jpg',
    '/static/avatars/avatar6.jpg',
    '/static/avatars/avatar7.jpg',
    '/static/avatars/avatar8.jpg',
    '/static/avatars/avatar9.jpg'
]

# Катастрофы (обнови пути под свои файлы)
CATASTROPHE_IMAGES = {
    'Ядерная война: высокий уровень радиации, разрушенная инфраструктура, дефицит пищи и воды.': '/static/catastrophes/nuclear.jpg',
    'Пандемия смертельного вируса: высокая заразность, нужны медики и антибиотики, иммунитет критичен.': '/static/catastrophes/pandemic.jpg',
    'Зомби-апокалипсис: орды нежити, нужны оружие и навыки выживания, здоровье важно.': '/static/catastrophes/zombie.jpg',
    'Глобальное потепление и наводнения: затопленные земли, нужны инженеры и фермеры.': '/static/catastrophes/flood.jpg',
    'Падение астероида: пыль в атмосфере, холод, дефицит света — нужны семена и садоводство.': '/static/catastrophes/asteroid.jpg',
    'Инопланетное вторжение: враждебные пришельцы, нужны военные и технологии.': '/static/catastrophes/alien.jpg',
    'Супервулкан: пепел в небе, ядерная зима, нужны запасы еды и тепла.': '/static/catastrophes/volcano.jpg',
    'Кибератака: отключение электричества, нужны программисты и генераторы.': '/static/catastrophes/cyber.jpg',
    'Химическая катастрофа: токсичные облака, нужны противогазы и химики.': '/static/catastrophes/chemical.jpg',
    'Землетрясения и цунами: разрушенные города, нужны строители и медики.': '/static/catastrophes/tsunami.jpg',
    'Магнитный сдвиг полюсов: хаос в навигации, радиация, нужны ученые.': '/static/catastrophes/magnetic.jpg',
    'Биологическая война: мутировавшие организмы, нужны биологи и вакцины.': '/static/catastrophes/bio_war.jpg',
}

cards_state = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/open_card', methods=['POST'])
def open_card():
    data = request.json
    print("Получены данные от бота:", data)

    player_id = data.get('player_id')
    username = data.get('username', '???')
    action = data.get('action')

    if not player_id:
        return jsonify({"status": "error"}), 400

    if action == "init":
        if player_id not in cards_state:
            avatar_index = int(hashlib.md5(str(player_id).encode()).hexdigest(), 16) % len(AVATARS)
            avatar_url = AVATARS[avatar_index]

            cards_state[player_id] = {
                "player_id": player_id,           # ← важно!
                "username": username,
                "avatar": avatar_url,
                "catastrophe_image": '/static/catastrophes/default.jpg',   # пока заглушка
                "categories": {
                    "gender_age": {"label": "Пол / Возраст", "value": "????"},
                    "profession": {"label": "Профессия", "value": "????"},
                    "health": {"label": "Здоровье", "value": "????"},
                    "baggage": {"label": "Багаж", "value": "????"},
                    "hobby": {"label": "Хобби / Навык", "value": "????"},
                    "secret": {"label": "Секрет", "value": "????"},
                    "chance": {"label": "Шанс выживания", "value": "????"}
                }
            }

        socketio.emit('create_card', cards_state[player_id])
        print(f"Отправлено create_card для {username} ({player_id})")
        return jsonify({"status": "success"}), 200

    # Обновление категории
    category = data.get('category')
    label = data.get('label')
    value = data.get('value')

    if category and value is not None:
        if player_id in cards_state and category in cards_state[player_id]["categories"]:
            cards_state[player_id]["categories"][category]["value"] = value

        socketio.emit('update_category', {
            "player_id": player_id,
            "category": category,
            "label": label,
            "value": value
        })
        print(f"Обновлена категория {category} для {player_id}")

    return jsonify({"status": "success"}), 200


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
