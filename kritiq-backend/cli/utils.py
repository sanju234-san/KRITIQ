import os
import json
import re
import sys
import fnmatch
import typer


def detect_language(path: str) -> str:
    """
    Detects the programming language of a file based on its extension.
    Defaults to 'python' if the extension is unrecognized.
    """
    _, ext = os.path.splitext(path)
    ext = ext.lower()

    extension_map = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".go": "go",
        ".java": "java",
        ".rs": "rust",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".rb": "ruby",
        ".php": "php",
        ".swift": "swift",
        ".kt": "kotlin",
        ".cs": "csharp",
        ".sh": "bash",
        ".sql": "sql",
    }
    return extension_map.get(ext, "python")


def load_kritiq_config() -> dict:
    """Loads .kritiq.json from current working directory or returns defaults."""
    config_path = os.path.join(os.getcwd(), ".kritiq.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "version": "2.4.12-stable",
        "engine": "gemini-2.5-flash",
        "max_file_size_kb": 500,
        "rules": ["security", "performance", "code_smells"],
    }


def load_kritiq_ignore() -> list[str]:
    """Loads .kritiqignore rules from current working directory."""
    ignore_path = os.path.join(os.getcwd(), ".kritiqignore")
    if not os.path.exists(ignore_path):
        return []
    try:
        with open(ignore_path, "r", encoding="utf-8") as f:
            return [
                line.strip()
                for line in f
                if line.strip() and not line.startswith("#")
            ]
    except Exception:
        return []


def is_ignored(file_path: str, ignore_patterns: list[str]) -> bool:
    """Checks if a file path matches any .kritiqignore pattern."""
    normalized_path = file_path.replace("\\", "/")
    basename = os.path.basename(normalized_path)

    for pattern in ignore_patterns:
        pattern = pattern.strip().replace("\\", "/")
        if pattern.endswith("/"):
            clean_pat = pattern.rstrip("/")
            if f"/{clean_pat}/" in f"/{normalized_path}/" or normalized_path.startswith(f"{clean_pat}/"):
                return True
        if fnmatch.fnmatch(basename, pattern) or fnmatch.fnmatch(normalized_path, pattern):
            return True
    return False


def sanitize_error(error: Exception | str) -> str:
    """Strips API keys and auth tokens from error strings before printing."""
    msg = str(error)
    msg = re.sub(r"(key|token|secret|auth)[=:]\s*['\"]?\S+['\"]?", r"\1=***", msg, flags=re.IGNORECASE)
    msg = re.sub(r"Bearer\s+[A-Za-z0-9\-\._~\+\/]+=*", "Bearer ***", msg, flags=re.IGNORECASE)
    return msg


def safe_check() -> str:
    """Returns ✔ if terminal stdout supports UTF-8, else [OK]."""
    encoding = getattr(sys.stdout, "encoding", "") or ""
    return "✔" if "utf" in encoding.lower() else "[OK]"


def safe_cross() -> str:
    """Returns ✖ if terminal stdout supports UTF-8, else [FAIL]."""
    encoding = getattr(sys.stdout, "encoding", "") or ""
    return "✖" if "utf" in encoding.lower() else "[FAIL]"


def safe_print(text: str):
    """Safely prints text replacing unsupported terminal characters."""
    encoding = getattr(sys.stdout, "encoding", "utf-8") or "utf-8"
    safe_text = text.encode(encoding, errors="replace").decode(encoding)
    typer.echo(safe_text)
