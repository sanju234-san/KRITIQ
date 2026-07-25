import os
import requests
from dotenv import load_dotenv
from repo_integration.local_clone import LocalCloneManager

load_dotenv()

GITHUB_API_BASE = "https://api.github.com"

_GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

if _GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {_GITHUB_TOKEN}"
    print("GitHub API: authenticated (5,000 req/hour, private repo access enabled)")
else:
    print("GitHub API: using unauthenticated requests (60/hour limit)")


def list_repo_files(owner: str, repo: str, path: str = "") -> list[str]:
    """
    Calls the GitHub REST API to list files and directories at the given path.
    If the REST API fails, times out, or hits rate limits, falls back to cloning
    the repository via LocalCloneManager (GitPython).
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"
    use_fallback = False

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
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
            cloned_dir = LocalCloneManager.clone_from(repo_url, token=_GITHUB_TOKEN)
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
