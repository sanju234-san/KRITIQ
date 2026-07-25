import os
import subprocess
import requests
import typer
from cli.auth import retrieve_token
from cli.utils import (
    load_kritiq_config,
    load_kritiq_ignore,
    sanitize_error,
    safe_cross,
    safe_check,
    safe_print
)


def diff(
    ref: str = typer.Argument("HEAD", help="Git reference or commit to diff against (default: HEAD)")
):
    """
    Review only changed lines from a specific Git reference via Kritiq Cloud API.
    """
    token = retrieve_token()
    if not token:
        typer.secho(f"{safe_cross()} Not authenticated. Run 'kritiq login' first.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Scanning git diff against '{ref}'...\n")

    try:
        result = subprocess.run(
            ["git", "diff", ref],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        diff_text = result.stdout or ""
    except Exception as e:
        typer.secho(f"{safe_cross()} Error running git diff: {sanitize_error(e)}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    if not diff_text.strip():
        typer.secho(f"{safe_check()} No uncommitted or modified line changes detected.", fg=typer.colors.GREEN)
        return

    # Cap diff patch size to 15k chars for AI token limits
    if len(diff_text) > 15000:
        diff_text = diff_text[:15000] + "\n\n# ... [Diff patch truncated for AI review token limit] ..."

    typer.echo("Analyzing diff patch with AI Engine...\n")

    try:
        resp = requests.post(
            "http://localhost:8000/reviews/",
            json={
                "code": diff_text,
                "language": "gitpatch",
                "filename": f"diff_{ref}.patch",
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=60
        )
        if resp.status_code == 401:
            typer.secho(f"{safe_cross()} Session expired. Run 'kritiq login' again.", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1)

        if resp.status_code != 200:
            detail = resp.json().get("detail", "Diff review failed.") if resp.headers.get("content-type") == "application/json" else resp.text
            typer.secho(f"{safe_cross()} Diff review failed: {sanitize_error(detail)}", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1)

        data = resp.json()
        raw_output = data.get("raw_output") or data.get("summary") or ""
        safe_print(raw_output)

    except (typer.Exit, SystemExit):
        raise
    except requests.exceptions.ConnectionError:
        typer.secho(f"{safe_cross()} Error: Cannot connect to Kritiq backend server on http://localhost:8000.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"{safe_cross()} Error analyzing diff: {sanitize_error(e)}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
