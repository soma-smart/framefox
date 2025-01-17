import os
import typer

import importlib.resources as pkg_resources
import framefox.terminal.commands
import framefox.terminal.commands.create
import framefox.terminal.commands.orm


class CommandHandler:
    def __init__(self):
        self.project_init = os.path.exists("src")
        self.priority_list = [
            'hello',
            'init',
            'create_entity',
            'create',
            'orm',
        ]

    @staticmethod
    def register_command(app: typer.Typer, command_instance):
        app.command(name=command_instance.name)(command_instance.execute)

    def load_commands(self, app_dict):
        # to_ignore = [
        #     'abstract_command.py',
        #     'unsupported_command.py',
        # ]
        # , commands_dir='../framefox/terminal/commands'
        # commands_dir = pkg_resources.files(framefox.terminal.commands)
        # for filename in self.custom_sort(os.listdir(commands_dir)):
        #     if filename.endswith('_command.py') and filename not in to_ignore:
        #         if not self.project_init and (filename == 'init_command.py' or filename == 'hello_world_command.py'):
        #             self.load_unique_command(app, filename)
        #         elif self.project_init and filename != 'init_command.py' and filename != 'hello_world_command.py':
        #             self.load_unique_command(app, filename)
        main_commands_dir = pkg_resources.files(framefox.terminal.commands)
        self.load_commands_for_an_app(app_dict["main"], main_commands_dir)

        orm_commands_dir = pkg_resources.files(framefox.terminal.commands.orm)
        self.load_commands_for_an_app(app_dict["orm"], orm_commands_dir, 'orm')

        create_commands_dir = pkg_resources.files(
            framefox.terminal.commands.create)
        self.load_commands_for_an_app(
            app_dict["create"], create_commands_dir, 'create')

    def load_commands_for_an_app(self, app: typer.Typer, commands_dir, dir=None):
        """
        Load commands for a specific app.
        """
        to_ignore = [
            'abstract_command.py',
            'unsupported_command.py',
        ]
        for filename in self.custom_sort(os.listdir(commands_dir)):
            if filename.endswith('_command.py') and filename not in to_ignore:
                if not self.project_init and (filename == 'init_command.py' or filename == 'hello_world_command.py'):
                    self.load_unique_command(app, filename, dir)
                elif self.project_init and filename != 'init_command.py' and filename != 'hello_world_command.py':
                    self.load_unique_command(app, filename, dir)

    def load_unique_command(self, app: typer.Typer, filename: str, dir: str = None):
        module_name = filename[:-3]
        if dir:
            module = __import__(f'framefox.terminal.commands.{dir}.{
                                module_name}', fromlist=[module_name])
        else:
            module = __import__(f'framefox.terminal.commands.{
                                module_name}', fromlist=[module_name])
        class_name = ''.join(word.capitalize()
                             for word in module_name.split('_'))
        command_class = getattr(module, class_name)
        command_instance = command_class()
        CommandHandler.register_command(app, command_instance)

    def custom_sort(self, command_files):
        """
        Sorts command files according to the priority list.
        Commands starting with prefixes in the priority list are sorted according to the order of this list.
        Other commands are sorted alphabetically and added at the end.
        """
        def sort_key(filename):
            # Extract the command name without the '_command.py' suffix
            base_name = filename[:-11]

            for index, prefix in enumerate(self.priority_list):
                if base_name.startswith(prefix):
                    # Return a tuple with the priority index and the rest of the name for secondary alphabetical sorting
                    return (index, base_name)

            # If no prefix matches, assign a high priority and sort alphabetically
            return (len(self.priority_list), base_name)
        return sorted(command_files, key=sort_key)
