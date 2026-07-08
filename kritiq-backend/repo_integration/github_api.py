import requests

GITHUB_API_BASE = "https://api.github.com"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def list_repo_files(owner: str, repo: str, path: str = "") -> list[str]:
    """
    Calls the GitHub REST API to list files and directories at the given
    path inside a public repository. Returns a list of entry names.
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
    except requests.exceptions.ConnectionError:
        return ["Error: could not connect to GitHub API — check your network connection."]
    except requests.exceptions.Timeout:
        return ["Error: request to GitHub API timed out."]

    if response.status_code == 404:
        return ["Error: repository or path not found."]

    if response.status_code == 403:
        # Distinguish rate-limit responses from other 403s
        if int(response.headers.get("X-RateLimit-Remaining", -1)) == 0:
            reset_ts = response.headers.get("X-RateLimit-Reset", "unknown")
            return [f"Error: GitHub API rate limit exceeded. Quota resets at Unix timestamp {reset_ts}."]
        return ["Error: access forbidden — the repository may be private or the request was blocked."]

    if response.status_code != 200:
        return [f"Error: unexpected GitHub API response {response.status_code}."]

    data = response.json()

    # /contents/ returns a list when path is a directory, dict when a single file
    if isinstance(data, dict):
        return [data.get("name", "")]

    return [entry["name"] for entry in data]
