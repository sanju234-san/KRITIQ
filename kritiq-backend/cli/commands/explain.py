import os
import typer
from ai_agent.explanation_service import explain_code
from ai_agent.walkthrough_writer import write_explanation_walkthrough
from cli.utils import detect_language


def explain(
    path: str = typer.Argument(..., help="Path to the file to explain")
):
    """
    Explain what a code file does in plain language using the Gemini AI agent.
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

    # Run code explanation
    try:
        typer.echo(f"Explaining {path} (detected language: {language})...\n")
        explanation_result = explain_code(code_content, language, file_path=path)
        typer.echo(explanation_result)
        saved_path = write_explanation_walkthrough(path, language, explanation_result)
        if saved_path:
            typer.echo(f"\nExplanation walkthrough saved to: {saved_path}")
    except Exception as e:
        typer.echo(f"Error during code explanation: {e}", err=True)
        raise typer.Exit(code=1)
