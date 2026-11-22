import os
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".kritiq"
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULT_API_URL = "https://kritiq.onrender.com"


def get_api_url() -> str:
    """
    Returns the Kritiq API base URL (env KRITIQ_API_URL > config.json > deployed Render URL).
    """
    env_url = os.environ.get("KRITIQ_API_URL", "").strip()
    if env_url:
        return env_url.rstrip("/")
    cfg = get_config()
    cfg_url = (cfg.get("api_url") or "").strip()
    if cfg_url:
        return cfg_url.rstrip("/")
    return DEFAULT_API_URL


def store_token(token: str, email: str = "", api_url: str = None):
    """
    Stores JWT session token in ~/.kritiq/config.json
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    existing = get_config()
    existing.update({
        "access_token": token,
        "email": email,
        "api_url": (api_url or get_api_url()).rstrip("/")
    })
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)


def store_repo(repo_owner: str, repo_name: str, repo_url: str = ""):
    """
    Stores the active connected repository in ~/.kritiq/config.json
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    existing = get_config()
    existing.update({
        "repo_owner": repo_owner,
        "repo_name": repo_name,
        "repo_url": repo_url,
    })
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)


def get_connected_repo() -> dict:
    """
    Returns {"repo_owner": ..., "repo_name": ..., "repo_url": ...} if connected, else {}.
    """
    cfg = get_config()
    if cfg.get("repo_owner") and cfg.get("repo_name"):
        return {
            "repo_owner": cfg["repo_owner"],
            "repo_name": cfg["repo_name"],
            "repo_url": cfg.get("repo_url", ""),
        }
    return {}

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
