import os
import requests
from dotenv import load_dotenv
from repo_integration.local_clone import LocalCloneManager

load_dotenv()

GITHUB_API_BASE = "https://api.github.com"

_GLOBAL_GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

_GITHUB_BASE_HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

if _GLOBAL_GITHUB_TOKEN:
    print("GitHub API: shared fallback GITHUB_TOKEN present. Preferring per-user OAuth tokens when available.")
else:
    print("GitHub API: no shared GITHUB_TOKEN; unauthenticated or per-user OAuth tokens only.")


def get_user_github_token(current_user: dict | None) -> str | None:
    if isinstance(current_user, dict):
        t = current_user.get("github_access_token")
        if isinstance(t, str) and t:
            return t
    return None


def get_github_headers(current_user: dict | None = None) -> dict:
    headers = dict(_GITHUB_BASE_HEADERS)
    user_token = get_user_github_token(current_user)
    if user_token:
        headers["Authorization"] = f"Bearer {user_token}"
        return headers
    if _GLOBAL_GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {_GLOBAL_GITHUB_TOKEN}"
    return headers


def list_repo_files(owner: str, repo: str, path: str = "", current_user: dict | None = None) -> list[str]:
    headers = get_github_headers(current_user)
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"
    use_fallback = False
    token_for_clone = get_user_github_token(current_user) or _GLOBAL_GITHUB_TOKEN

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                return [data.get("name", "")]
            return [entry["name"] for entry in data]
        elif response.status_code == 403 and int(response.headers.get("X-RateLimit-Remaining", -1)) == 0:
            print("[FALLBACK] GitHub REST API rate limit reached — falling back to LocalCloneManager...")
            use_fallback = True
        elif response.status_code == 404:
            return ["Error: repository or path not found."]
        else:
            use_fallback = True
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        print(f"[FALLBACK] GitHub REST API error ({e}) — falling back to LocalCloneManager...")
        use_fallback = True

    if use_fallback:
        repo_url = f"https://github.com/{owner}/{repo}.git"
        try:
            cloned_dir = LocalCloneManager.clone_from(repo_url, token=token_for_clone)
            target_path = os.path.join(cloned_dir, path) if path else cloned_dir
            if os.path.exists(target_path) and os.path.isdir(target_path):
                files = os.listdir(target_path)
                LocalCloneManager.cleanup(cloned_dir)
                return files
            LocalCloneManager.cleanup(cloned_dir)
            return ["Error: path not found in cloned repository."]
        except Exception as clone_err:
            return [f"Error: GitHub API and LocalCloneManager fallback both failed ({clone_err})."]

    return ["Error: could not retrieve repository contents."]
