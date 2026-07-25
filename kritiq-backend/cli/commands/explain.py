import os
import requests
import typer
from cli.auth import retrieve_token
from cli.utils import (
    detect_language,
    load_kritiq_config,
    load_kritiq_ignore,
    is_ignored,
    sanitize_error,
    safe_cross,
    safe_print
)
from ai_agent.walkthrough_writer import write_explanation_walkthrough


def explain(
    path: str = typer.Argument(..., help="Path to the file to explain")
):
    """
    Explain what a code file does in plain language via Kritiq Cloud API.
    """
    token = retrieve_token()
    if not token:
        typer.secho(f"{safe_cross()} Not authenticated. Run 'kritiq login' first.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    if not os.path.exists(path):
        typer.secho(f"{safe_cross()} Error: File '{path}' does not exist.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    if os.path.isdir(path):
        typer.secho(f"{safe_cross()} Error: '{path}' is a directory. Please provide a file path.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    # Check .kritiqignore
    ignore_patterns = load_kritiq_ignore()
    if is_ignored(path, ignore_patterns):
        typer.secho(f"[SKIP] Skipped: '{path}' matches .kritiqignore", fg=typer.colors.YELLOW)
        return

    # Check file size limit
    config = load_kritiq_config()
    max_size_kb = config.get("max_file_size_kb", 500)
    file_size_kb = os.path.getsize(path) / 1024.0
    if file_size_kb > max_size_kb:
        typer.secho(f"{safe_cross()} File '{path}' exceeds max size limit ({file_size_kb:.1f}KB > {max_size_kb}KB). Skipping.", fg=typer.colors.YELLOW)
        return

    try:
        with open(path, "r", encoding="utf-8") as f:
            code_content = f.read()
    except Exception as e:
        typer.secho(f"{safe_cross()} Error reading file: {sanitize_error(e)}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    language = detect_language(path)
    typer.echo(f"Explaining {path} (detected language: {language})...\n")

    try:
        resp = requests.post(
            "http://localhost:8000/explanations/",
            json={
                "code": code_content,
                "language": language,
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=60
        )
        if resp.status_code == 401:
            typer.secho(f"{safe_cross()} Session expired. Run 'kritiq login' again.", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1)

        if resp.status_code != 200:
            detail = resp.json().get("detail", "Explanation request failed.") if resp.headers.get("content-type") == "application/json" else resp.text
            typer.secho(f"{safe_cross()} Explanation failed: {sanitize_error(detail)}", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1)

        data = resp.json()
        explanation_result = data.get("explanation", "")

        safe_print(explanation_result)

        try:
            saved_path = write_explanation_walkthrough(path, language, explanation_result)
            if saved_path:
                typer.secho(f"\nExplanation walkthrough saved to: {saved_path}", fg=typer.colors.GREEN)
        except Exception:
            pass

    except (typer.Exit, SystemExit):
        raise
    except requests.exceptions.ConnectionError:
        typer.secho(f"{safe_cross()} Error: Cannot connect to Kritiq backend server on http://localhost:8000.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"{safe_cross()} Error during code explanation: {sanitize_error(e)}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
