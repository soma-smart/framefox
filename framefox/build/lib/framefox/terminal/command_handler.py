import os
# import importlib.util
import typer

# from framefox.terminal.commands.abstract_command import AbstractCommand
# from framefox.terminal.commands.unsupported_command import UnsupportedCommand

import importlib.resources as pkg_resources
import framefox.terminal.commands


class CommandHandler:
    @staticmethod
    def register_command(app: typer.Typer, command_instance):
        app.command(name=command_instance.name)(command_instance.execute)

    @staticmethod
    def load_commands(app: typer.Typer):
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
                # file_path = os.path.join(commands_dir, filename)
                # Import the module and register the command
                module = __import__(f'framefox.terminal.commands.{
                                    module_name}', fromlist=[module_name])
                class_name = ''.join(word.capitalize()
                                     for word in module_name.split('_'))
                command_class = getattr(module, class_name)
                command_instance = command_class()
                CommandHandler.register_command(app, command_instance)
                # spec = importlib.util.spec_from_file_location(
                #     module_name, file_path)
                # module = importlib.util.module_from_spec(spec)
                # spec.loader.exec_module(module)
                # for attr in dir(module):
                #     cls = getattr(module, attr)
                #     if isinstance(cls, type) and \
                #             issubclass(cls, AbstractCommand) and \
                #             (cls is not AbstractCommand and cls is not UnsupportedCommand):
                #         CommandHandler.register_command(app, cls())
