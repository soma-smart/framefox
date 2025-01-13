import os
import importlib.util
import typer

from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.commands.unsupported_command import UnsupportedCommand


class CommandHandler:
    @staticmethod
    def register_command(app: typer.Typer, command_instance):
        app.command(name=command_instance.name)(command_instance.execute)

    @staticmethod
    def load_commands(app: typer.Typer, commands_dir='framefox/framefox/terminal/commands'):
        for filename in os.listdir(commands_dir):
            if filename.endswith('_command.py'):
                module_name = filename[:-3]
                file_path = os.path.join(commands_dir, filename)
                spec = importlib.util.spec_from_file_location(
                    module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for attr in dir(module):
                    cls = getattr(module, attr)
                    if isinstance(cls, type) and \
                            issubclass(cls, AbstractCommand) and \
                            (cls is not AbstractCommand and cls is not UnsupportedCommand):
                        CommandHandler.register_command(app, cls())
