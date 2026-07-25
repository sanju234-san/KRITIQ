import requests
import typer
from cli.auth import retrieve_token
from cli.utils import sanitize_error, safe_cross

def chat():
    """
    Start an interactive chat session with Kritiq via Kritiq Cloud API.
    """
    token = retrieve_token()
    if not token:
        typer.secho(f"{safe_cross()} Not authenticated. Run 'kritiq login' first.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    typer.secho("===================================================", fg=typer.colors.CYAN)
    typer.secho("         Welcome to the KRITIQ Chat Interface!     ", fg=typer.colors.CYAN, bold=True)
    typer.secho(" Ask questions about your code, reviews, or files.  ", fg=typer.colors.CYAN)
    typer.secho(" Type 'exit' or 'quit' to end the session.          ", fg=typer.colors.YELLOW)
    typer.secho("===================================================\n", fg=typer.colors.CYAN)

    conversation_history = []

    while True:
        try:
            user_input = typer.prompt("You")
            if user_input.strip().lower() in ("exit", "quit"):
                typer.secho("\nEnding chat session. Goodbye!", fg=typer.colors.GREEN)
                break

            if not user_input.strip():
                continue

            typer.echo("Kritiq is thinking...")

            resp = requests.post(
                "http://localhost:8000/chat/",
                json={
                    "user_message": user_input,
                    "history": conversation_history,
                },
                headers={"Authorization": f"Bearer {token}"},
                timeout=60
            )

            if resp.status_code == 401:
                typer.secho(f"\n{safe_cross()} Session expired. Run 'kritiq login' again.", fg=typer.colors.RED, err=True)
                break

            if resp.status_code != 200:
                detail = resp.json().get("detail", "Chat error occurred.") if resp.headers.get("content-type") == "application/json" else resp.text
                typer.secho(f"\n{safe_cross()} Error: {sanitize_error(detail)}", fg=typer.colors.RED, err=True)
                continue

            data = resp.json()
            response_text = data.get("response", "")
            conversation_history = data.get("history", [])

            typer.echo("")
            typer.secho("Kritiq:", fg=typer.colors.MAGENTA, bold=True)
            typer.echo(response_text)
            typer.echo("")

        except KeyboardInterrupt:
            typer.secho("\n\nEnding chat session. Goodbye!", fg=typer.colors.GREEN)
            break
        except requests.exceptions.ConnectionError:
            typer.secho(f"\n{safe_cross()} Error: Cannot connect to Kritiq backend server on http://localhost:8000.", fg=typer.colors.RED, err=True)
            break
        except Exception as e:
            typer.secho(f"\nError occurred: {sanitize_error(e)}", fg=typer.colors.RED, err=True)
            typer.secho("Please try your question again.\n", fg=typer.colors.YELLOW)
