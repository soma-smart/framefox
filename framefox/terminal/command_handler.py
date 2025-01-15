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
        if self.project_init:
            to_ignore = [
                'abstract_command.py',
                'orm_create_db_command.py',
                'orm_migrate_db_command.py',
            ]
        else:
            to_ignore = [
                'abstract_command.py',
                'orm_create_db_command.py',
                'orm_migrate_db_command.py',
            ]
        # , commands_dir='../framefox/terminal/commands'
        commands_dir = pkg_resources.files(framefox.terminal.commands)
        for filename in os.listdir(commands_dir):
            if filename.endswith('_command.py') and filename not in to_ignore:
                module_name = filename[:-3]
                # Import the module and register the command
                module = __import__(f'framefox.terminal.commands.{
                                    module_name}', fromlist=[module_name])
                class_name = ''.join(word.capitalize()
                                     for word in module_name.split('_'))
                command_class = getattr(module, class_name)
                command_instance = command_class()
                CommandHandler.register_command(app, command_instance)
