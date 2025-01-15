import os
import typer

import importlib.resources as pkg_resources
import framefox.terminal.commands


class CommandHandler:
    def __init__(self):
        self.project_init = os.path.exists("src")

    @staticmethod
    def register_command(app: typer.Typer, command_instance):
        app.command(name=command_instance.name)(command_instance.execute)

    def load_commands(self, app: typer.Typer):
        to_ignore = [
            'abstract_command.py',
            'add_property_command.py',
            'unsupported_command.py',
        ]
        # , commands_dir='../framefox/terminal/commands'
        commands_dir = pkg_resources.files(framefox.terminal.commands)
        for filename in sorted(os.listdir(commands_dir)):
            if filename.endswith('_command.py') and filename not in to_ignore:
                if not self.project_init and (filename == 'init_project_command.py' or filename == 'hello_world_command.py'):
                    self.load_unique_command(app, filename)
                elif self.project_init and filename != 'init_project_command.py' and filename != 'hello_world_command.py':
                    self.load_unique_command(app, filename)

    def load_unique_command(self, app: typer.Typer, filename: str):
        module_name = filename[:-3]
        module = __import__(f'framefox.terminal.commands.{
                            module_name}', fromlist=[module_name])
        class_name = ''.join(word.capitalize()
                             for word in module_name.split('_'))
        command_class = getattr(module, class_name)
        command_instance = command_class()
        CommandHandler.register_command(app, command_instance)
