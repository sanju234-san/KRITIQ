import requests
import typer
from cli.auth import retrieve_token, get_api_url, store_repo
from cli.utils import sanitize_error, safe_check, safe_cross


def connect(
    repo_url: str = typer.Argument(..., help="GitHub repository URL, e.g. https://github.com/owner/repo")
):
    """
    Connect a GitHub repository to Kritiq for context-aware reviews and translations.
    """
    token = retrieve_token()
    if not token:
        typer.secho(f"{safe_cross()} Not authenticated. Run 'kritiq login' first.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    api_url = get_api_url()
    typer.echo(f"Connecting repository {repo_url}...")

    try:
        resp = requests.post(
            f"{api_url}/repositories/connect",
            json={"repo_url": repo_url},
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )
        if resp.status_code == 401:
            typer.secho(f"{safe_cross()} Session expired. Run 'kritiq login' again.", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1)

        if resp.status_code not in (200, 201):
            detail = resp.json().get("detail", "Failed to connect repository.") if resp.headers.get("content-type") == "application/json" else resp.text
            typer.secho(f"{safe_cross()} Connect failed: {sanitize_error(detail)}", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1)

        data = resp.json()
        owner = data.get("owner") or ""
        name = data.get("name") or ""
        if not (owner and name):
            parts = repo_url.rstrip("/").removesuffix(".git").split("/")
            if len(parts) >= 2:
                owner, name = parts[-2], parts[-1]

        store_repo(owner, name, repo_url)
        typer.secho(f"{safe_check()} Connected repository {owner}/{name}.", fg=typer.colors.GREEN, bold=True)
        typer.echo("You can now run 'kritiq review <file_path>' or 'kritiq translate <file_path> --to <lang>'.")

    except (typer.Exit, SystemExit):
        raise
    except requests.exceptions.ConnectionError:
        typer.secho(f"{safe_cross()} Error: Cannot connect to Kritiq backend server on {api_url}.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"{safe_cross()} Error connecting repository: {sanitize_error(e)}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
