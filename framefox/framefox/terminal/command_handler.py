import os
import importlib.util

from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.commands.unsupported_command import UnsupportedCommand

# import inspect
# from pathlib import Path
import typer


class CommandHandler:
    def __init__(self):
        self.commands = {}

    def register_command(self, app: typer.Typer, command_instance):
        # self.commands[command.name] = command
        # print(f"Registering command {command_instance.name}")
        # command_instance = obj()
        app.command(name=command_instance.name)(command_instance.execute)

    def load_commands(self, app: typer.Typer, commands_dir='framefox/framefox/terminal/commands'):
        for filename in os.listdir(commands_dir):
            # print(filename)
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
                        self.register_command(app, cls())

    def run(self, command_name, args):
        command = self.commands.get(command_name, UnsupportedCommand())
        command.execute(*args)


# def load_commands(app: typer.Typer, commands_path: str = "framefox/terminal/commands"):
#     commands_dir = Path(commands_path)
#     for file in commands_dir.glob("*.py"):
#         module_name = file.stem
#         module = importlib.import_module(f"{commands_path}.{module_name}")
#         for name, obj in inspect.getmembers(module, inspect.isclass):
#             if hasattr(obj, 'execute') and hasattr(obj, 'name'):
#                 print(f"Registering command {obj.name}")
#                 command_instance = obj()
#                 app.command(name=command_instance.name)(
#                     command_instance.execute)


# def load_commands(self, commands_dir='framefox/terminal/commands'):
#     for filename in os.listdir(commands_dir):
#         if filename.endswith('_command.py'):
#             module_name = filename[:-3]
#             file_path = os.path.join(commands_dir, filename)
#             spec = importlib.util.spec_from_file_location(
#                 module_name, file_path)
#             module = importlib.util.module_from_spec(spec)
#             spec.loader.exec_module(module)
#             for attr in dir(module):
#                 cls = getattr(module, attr)
#                 if isinstance(cls, type) and \
#                         issubclass(cls, AbstractCommand) and \
#                         (cls is not AbstractCommand and cls is not UnsupportedCommand):
#                     self.register_command(cls())


# # Example usage
# if __name__ == "__main__":
#     app = typer.Typer()
#     load_commands(app)
#     app()
