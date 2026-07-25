# Sanjeevni domain - CLI application entrypoint using Typer
import typer

from cli.commands.review import review
from cli.commands.translate import translate
from cli.commands.explain import explain
from cli.commands.chat import chat
from cli.commands.login import login
from cli.commands.init import init
from cli.commands.diff import diff

app = typer.Typer(help="Kritiq Command Line Interface")

# Register commands per documentation
app.command(name="login")(login)
app.command(name="init")(init)
app.command(name="diff")(diff)
app.command(name="review")(review)
app.command(name="translate")(translate)
app.command(name="explain")(explain)
app.command(name="chat")(chat)

if __name__ == "__main__":
    app()
