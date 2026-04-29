# config.py - Configuration and constants for Snake Game (TSIS 4)
# Contains window dimensions, colors, game speed settings, and settings file handling

import json
import os

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Full path to settings.json file (saved in the same folder as the script)
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

# Default game settings (used when settings.json is missing)
DEFAULT_SETTINGS = {
    "snake_color": [0, 255, 0],      # initial snake color (green)
    "grid_overlay": True,            # whether to draw grid lines
    "sound": True                    # sound effects on/off
}

# Window and cell dimensions
WIDTH, HEIGHT = 800, 600              # game window size in pixels
BLOCK_SIZE = 20                       # size of each grid cell (snake segment)
BASE_SPEED = 3                        # initial snake speed (frames per second)

# Color definitions (RGB tuples)
C_BG = (30, 30, 30)                 # background color of the game area
C_GRID = (50, 50, 50)               # grid line color
C_FOOD_NORMAL = (200, 0, 0)         # normal food color (red)
C_FOOD_WEIGHTED = (255, 215, 0)     # weighted/golden food color (yellow)
C_POISON = (139, 0, 0)              # poison food color (dark red)
C_OBSTACLE = (100, 100, 100)        # obstacle block color (gray)
C_PW_SPEED = (0, 255, 255)          # speed‑boost power‑up color (cyan)
C_PW_SLOW = (0, 0, 255)             # slow‑motion power‑up color (blue)
C_PW_SHIELD = (255, 0, 255)         # shield power‑up color (magenta)

def load_settings():
    """
    Load user settings from settings.json.
    If the file does not exist or is corrupted, create it with default settings.
    Also add any missing keys from DEFAULT_SETTINGS to the existing file.
    """
    # If settings file doesn't exist, create default and return it
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS
    try:
        # Read existing settings
        with open(SETTINGS_FILE, "r") as f:
            user_settings = json.load(f)
        # Check if any default keys are missing (e.g., after an update)
        updated = False
        for key, value in DEFAULT_SETTINGS.items():
            if key not in user_settings:
                user_settings[key] = value
                updated = True
        # If we added missing keys, save the updated settings
        if updated:
            save_settings(user_settings)
        return user_settings
    except (json.JSONDecodeError, Exception):
        # If the file is corrupt, overwrite with defaults
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS

def save_settings(settings):
    """
    Save the given settings dictionary to settings.json in pretty-printed format.
    """
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)