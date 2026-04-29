import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "snake_color": [0, 255, 0],
    "grid_overlay": True,
    "sound": True
}

# Размеры окна и блоков
WIDTH, HEIGHT = 800, 600
BLOCK_SIZE = 20
BASE_SPEED = 3

# Цвета
C_BG = (30, 30, 30)
C_GRID = (50, 50, 50)
C_FOOD_NORMAL = (200, 0, 0)
C_FOOD_WEIGHTED = (255, 215, 0)
C_POISON = (139, 0, 0)
C_OBSTACLE = (100, 100, 100)
C_PW_SPEED = (0, 255, 255)
C_PW_SLOW = (0, 0, 255)
C_PW_SHIELD = (255, 0, 255)

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS
    try:
        with open(SETTINGS_FILE, "r") as f:
            user_settings = json.load(f)
        updated = False
        for key, value in DEFAULT_SETTINGS.items():
            if key not in user_settings:
                user_settings[key] = value
                updated = True
        if updated:
            save_settings(user_settings)
        return user_settings
    except:
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)