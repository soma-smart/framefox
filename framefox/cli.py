import typer

from framefox.terminal.command_handler import CommandHandler

app = typer.Typer()
CommandHandler().load_commands(app)

if __name__ == "__main__":
    app()
