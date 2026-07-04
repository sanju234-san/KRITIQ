# Sanjeevni domain - CLI application entrypoint using Typer
import typer

app = typer.Typer(help="Kritiq Command Line Interface")

# Register commands
# TODO: Import and add subcommands

if __name__ == "__main__":
    app()
