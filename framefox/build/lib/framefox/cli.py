import typer
# from injectable import load_injection_container

from framefox.terminal.command_handler import CommandHandler

# load_injection_container()
app = typer.Typer()
CommandHandler.load_commands(app)

if __name__ == "__main__":
    app()
