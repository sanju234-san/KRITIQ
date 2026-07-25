import os
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".kritiq"
CONFIG_FILE = CONFIG_DIR / "config.json"

def store_token(token: str, email: str = ""):
    """
    Stores JWT session token in ~/.kritiq/config.json
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config_data = {
        "access_token": token,
        "email": email,
        "api_url": "http://localhost:8000"
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)

def retrieve_token() -> str:
    """
    Retrieves stored access token from ~/.kritiq/config.json
    """
    if not CONFIG_FILE.exists():
        return ""
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("access_token", "")
    except Exception:
        return ""

def get_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}
