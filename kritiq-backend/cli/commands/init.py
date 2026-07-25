import os
import json
import typer
from cli.utils import safe_check

def init():
    """
    Initialize Kritiq configuration and .kritiqignore in the current directory.
    """
    config_path = ".kritiq.json"
    ignore_path = ".kritiqignore"

    config_data = {
        "version": "2.4.12-stable",
        "engine": "gemini-2.5-flash",
        "max_file_size_kb": 500,
        "rules": ["security", "performance", "code_smells"]
    }

    ignore_defaults = """# Kritiq Ignore Rules
node_modules/
dist/
build/
.git/
venv/
__pycache__/
*.min.js
*.pyc
"""

    if not os.path.exists(config_path):
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)
        typer.secho(f"{safe_check()} Created .kritiq.json project configuration.", fg=typer.colors.GREEN)
    else:
        typer.echo("[INFO] .kritiq.json already exists.")

    if not os.path.exists(ignore_path):
        with open(ignore_path, "w", encoding="utf-8") as f:
            f.write(ignore_defaults)
        typer.secho(f"{safe_check()} Created .kritiqignore file.", fg=typer.colors.GREEN)
    else:
        typer.echo("[INFO] .kritiqignore already exists.")

    typer.secho(f"{safe_check()} Kritiq workspace initialized successfully!", fg=typer.colors.GREEN, bold=True)
