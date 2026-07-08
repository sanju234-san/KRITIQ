import os
import typer
from ai_agent.translation_service import translate_code
from cli.utils import detect_language


def translate(
    path: str = typer.Argument(..., help="Path to the file to translate"),
    to: str = typer.Option(..., "--to", help="Target language for translation")
):
    """
    Translate a code file to another language using the Gemini AI agent.
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
    source_language = detect_language(path)

    # Run code translation
    try:
        typer.echo(f"Translating {path} (from {source_language} to {to})...\n")
        translation_result = translate_code(code_content, source_language, to)
        typer.echo(translation_result)
    except Exception as e:
        typer.echo(f"Error during code translation: {e}", err=True)
        raise typer.Exit(code=1)
