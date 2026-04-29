# persistence.py
import json
import os

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE = "settings.json"

# Настройки по умолчанию
DEFAULT_SETTINGS = {
    "sound": True,
    "car_color": "green",
    "difficulty": "normal",  # easy, normal, hard
    "player_name": "Player"
}

def load_leaderboard():
    """Загружает список лучших результатов из JSON."""
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    with open(LEADERBOARD_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return []

def save_leaderboard(entries):
    """Сохраняет топ-10 результатов (сортируются по убыванию очков)."""
    entries.sort(key=lambda x: x["score"], reverse=True)
    top10 = entries[:10]
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(top10, f, indent=2)

def add_score(name, score, distance):
    """Добавляет новый результат в лидерборд и сохраняет."""
    entries = load_leaderboard()
    entries.append({"name": name, "score": score, "distance": distance})
    save_leaderboard(entries)

def load_settings():
    """Загружает настройки, если файл отсутствует – создаёт с дефолтными."""
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()
    with open(SETTINGS_FILE, "r") as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)