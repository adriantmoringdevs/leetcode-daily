import json
from pathlib import Path

APP_SUPPORT_DIR = (
    Path.home()
    / "Library"
    / "Application Support"
    / "LeetCode Daily"
)

CONFIG_FILE = APP_SUPPORT_DIR / "config.json"


def save_username(username):
    APP_SUPPORT_DIR.mkdir(parents=True, exist_ok=True)

    with open(CONFIG_FILE, "w") as file:
        json.dump({"username": username}, file)


def load_username():
    if not CONFIG_FILE.exists():
        return None

    with open(CONFIG_FILE, "r") as file:
        data = json.load(file)

    return data.get("username")

