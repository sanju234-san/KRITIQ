import os
import shutil
import stat
import tempfile
import git


class LocalCloneManager:
    """
    Manages local Git repository cloning and file operations using GitPython.
    Serves as a robust fallback when the GitHub REST API is rate-limited or unreachable.
    """

    @staticmethod
    def clone_from(repo_url: str, target_dir: str = None, token: str = None) -> str:
        """
        Clones a remote Git repository to target_dir (or a fresh temporary directory).
        Injects optional auth token for private GitHub repositories.
        Returns the absolute local path to the cloned repository.
        """
        if not repo_url or not repo_url.strip():
            raise ValueError("Repository URL cannot be empty.")

        # Inject auth token if provided and URL is HTTPS
        formatted_url = repo_url.strip()
        if token and formatted_url.startswith("https://") and "@" not in formatted_url:
            formatted_url = formatted_url.replace("https://", f"https://{token}@")

        if not target_dir:
            target_dir = tempfile.mkdtemp(prefix="kritiq_clone_")

        os.makedirs(target_dir, exist_ok=True)

        try:
            git.Repo.clone_from(formatted_url, target_dir)
            return target_dir
        except git.exc.GitCommandError as e:
            # Clean up temp dir on failed clone
            LocalCloneManager.cleanup(target_dir)
            raise RuntimeError(f"Git clone failed: {e.stderr.strip() if e.stderr else str(e)}") from e
        except Exception as e:
            LocalCloneManager.cleanup(target_dir)
            raise RuntimeError(f"An unexpected error occurred during cloning: {e}") from e

    @staticmethod
    def read_local_file(repo_dir: str, relative_filepath: str) -> str:
        """
        Reads raw file contents from a cloned repository directory.
        """
        full_path = os.path.join(repo_dir, relative_filepath)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File '{relative_filepath}' not found in repository.")
        if os.path.isdir(full_path):
            raise IsADirectoryError(f"'{relative_filepath}' is a directory, not a file.")

        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    @staticmethod
    def cleanup(dir_path: str):
        """
        Safely removes a local cloned repository directory, handling Windows read-only file locks.
        """
        if not dir_path or not os.path.exists(dir_path):
            return

        def _remove_readonly(func, path, exc_info):
            os.chmod(path, stat.S_IWRITE)
            func(path)

        try:
            shutil.rmtree(dir_path, onerror=_remove_readonly)
        except Exception as e:
            print(f"[WARNING] Could not completely remove temp dir '{dir_path}': {e}")
