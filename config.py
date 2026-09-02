import json
import os

CONFIG_FILE = "config.json"

def save_username(username):
    data = {
        "username": username
    }

    with open(CONFIG_FILE, "w") as file:
        json.dump(data, file)

def load_username():
    if not os.path.exists(CONFIG_FILE):
        return None

    with open(CONFIG_FILE, "r") as file:
        data = json.load(file)

    return data.get("username")