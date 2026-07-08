import os
from repo_integration.github_api import list_repo_files


def list_local_files(directory: str = ".") -> list[str]:
    """
    Returns a list of filenames in the given local directory.
    """
    try:
        if not os.path.exists(directory):
            return [f"Error: Directory '{directory}' does not exist."]
        if not os.path.isdir(directory):
            return [f"Error: '{directory}' is not a directory."]
        return os.listdir(directory)
    except Exception as e:
        return [f"Error: {e}"]


def list_github_repo_files(owner: str, repo: str, path: str = "") -> list[str]:
    """
    Returns a list of file/directory names at the given path inside a
    public GitHub repository, using the GitHub REST API.
    """
    return list_repo_files(owner, repo, path)

