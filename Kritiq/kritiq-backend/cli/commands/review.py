import os
import typer
from ai_agent.review_service import review_code
from cli.utils import detect_language


def review(
    path: str = typer.Argument(..., help="Path to the file to review")
):
    """
    Review a code file using the Gemini AI agent.
    """
    if not os.path.exists(path):
        typer.echo(f"Error: File '{path}' does not exist.", err=True)
        raise typer.Exit(code=1)

    if os.path.isdir(path):
        typer.echo(f"Error: '{path}' is a directory. Please provide a file path.", err=True)
        raise typer.Exit(code=1)

    try:
        with open(path, "r", encoding="utf-8") as f:
            code_content = f.read()
    except Exception as e:
        typer.echo(f"Error reading file: {e}", err=True)
        raise typer.Exit(code=1)

    # Detect language
    language = detect_language(path)

    # Run code review
    try:
        typer.echo(f"Reviewing {path} (detected language: {language})...\n")
        review_result = review_code(code_content, language, file_path=path)
        typer.echo(review_result)
    except Exception as e:
        typer.echo(f"Error during code review: {e}", err=True)
        raise typer.Exit(code=1)

    # Generate walkthrough summary
    try:
        from ai_agent.walkthrough_writer import write_review_walkthrough
        write_review_walkthrough(path, language, review_result)
    except Exception as e:
        typer.echo(f"\n[Warning] Could not generate walkthrough file: {e}", err=True)

