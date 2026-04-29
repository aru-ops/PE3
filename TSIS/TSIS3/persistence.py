# persistence.py - Handles loading/saving settings and leaderboard to JSON files
import json
import os

# File names where settings and leaderboard are stored
SETTINGS_FILE = 'settings.json'
LEADERBOARD_FILE = 'leaderboard.json'

def load_settings():
    """
    Load user settings from settings.json.
    If the file does not exist or is corrupted, create default settings.
    """
    # Check if settings file already exists
    if os.path.exists(SETTINGS_FILE):
        # Open and read the JSON file
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)          # Parse JSON into a Python dictionary
    # If file doesn't exist, create default settings
    default = {"sound": True, "car_color": "red", "difficulty": "normal"}
    save_settings(default)               # Save defaults to file
    return default

def save_settings(settings):
    """
    Save the current settings dictionary to settings.json (pretty‑printed).
    """
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)   # Write JSON with indentation for readability

def load_leaderboard():
    """
    Load the leaderboard (top scores) from leaderboard.json.
    Returns a list of dictionaries, or an empty list if file does not exist.
    """
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'r') as f:
            return json.load(f)            # Parse JSON list
    return []                               # No scores yet

def save_score(name, score, distance):
    """
    Add a new score entry to the leaderboard, keep only top 10 scores,
    and save back to leaderboard.json.
    """
    board = load_leaderboard()              # Get current leaderboard
    # Append the new score
    board.append({"name": name, "score": score, "distance": distance})
    # Sort by score descending (highest first) and keep first 10
    board = sorted(board, key=lambda x: x['score'], reverse=True)[:10]
    # Write updated leaderboard back to file
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(board, f, indent=4)