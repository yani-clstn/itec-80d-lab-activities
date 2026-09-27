import json
import os

CONFIG_FILE = "config.json"
HISTORY_FILE = "bmi_history.json"


def load_preferences():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"theme": "light", "system": "Standard", "font_delta": 0}


def save_preferences(prefs):
    with open(CONFIG_FILE, "w") as f:
        json.dump(prefs, f, indent=4)


def save_history_record(record):
    history = load_history()
    history.append(record)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)


def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []