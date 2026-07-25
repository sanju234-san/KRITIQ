import typer
import requests
from cli.auth import store_token
from cli.utils import sanitize_error, safe_check, safe_cross

def login(
    email: str = typer.Option(None, "--email", "-e", help="Work Email address"),
    password: str = typer.Option(None, "--password", "-p", help="Account password (min 8 chars)")
):
    """
    Authenticate CLI with Kritiq Cloud service and store session token in ~/.kritiq/config.json.
    """
    if not email:
        email = typer.prompt("Enter Work Email")
    if not password:
        password = typer.prompt("Enter Password (min 8 chars)", hide_input=True)

    typer.echo("Logging into Kritiq Cloud...")

    try:
        resp = requests.post("http://localhost:8000/auth/login", json={"email": email, "password": password}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            token = data.get("access_token", "")
            store_token(token, email)
            typer.secho(f"{safe_check()} Success. Session token stored in ~/.kritiq/config.json", fg=typer.colors.GREEN, bold=True)
        else:
            detail = resp.json().get("detail", "Authentication failed.")
            if isinstance(detail, list):
                detail = "; ".join([d.get("msg", str(d)) for d in detail])
            detail = sanitize_error(detail)
            typer.secho(f"{safe_cross()} Login failed: {detail}", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1)
    except requests.exceptions.ConnectionError:
        typer.secho(f"{safe_cross()} Error: Cannot connect to Kritiq backend server on http://localhost:8000.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"{safe_cross()} Error: {sanitize_error(e)}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
