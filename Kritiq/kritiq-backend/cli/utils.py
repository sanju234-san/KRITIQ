import os


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
        ".java": "java",
    }
    return extension_map.get(ext, "python")
