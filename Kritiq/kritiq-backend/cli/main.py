# Sanjeevni domain - CLI application entrypoint using Typer
import typer

from cli.commands.review import review
from cli.commands.translate import translate
from cli.commands.explain import explain

app = typer.Typer(help="Kritiq Command Line Interface")

# Register commands
app.command(name="review")(review)
app.command(name="translate")(translate)
app.command(name="explain")(explain)

if __name__ == "__main__":
    app()
