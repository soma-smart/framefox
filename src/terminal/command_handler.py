import os
import importlib.util

from src.terminal.commands.abstract_command import AbstractCommand
from src.terminal.commands.unsupported_command import UnsupportedCommand


class CommandHandler:
    def __init__(self):
        self.commands = {}

    def register_command(self, command):
        self.commands[command.name] = command

    def load_commands(self, commands_dir='src/terminal/commands'):
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
                        self.register_command(cls())

    def run(self, command_name, args):
        command = self.commands.get(command_name, UnsupportedCommand())
        command.execute(*args)
