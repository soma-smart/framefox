import os
import typer

import importlib.resources as pkg_resources
import framefox.terminal.commands
import framefox.terminal.commands.create
import framefox.terminal.commands.orm
import framefox.terminal.commands.orm.database
import framefox.terminal.commands.server
import framefox.terminal.commands.debug
import framefox.terminal.commands.cache
import framefox.terminal.commands.fixtures


class CommandHandler:
    def __init__(self):
        self.project_init = os.path.exists("src")
        self.priority_list = [
            "init",
            "create_entity",
            "create",
            "orm",
        ]

    @staticmethod
    def register_command(app: typer.Typer, command_instance):
        app.command(name=command_instance.name)(command_instance.execute)

    def load_commands(self, app_dict):

        main_commands_dir = pkg_resources.files(framefox.terminal.commands)
        self.load_commands_for_an_app(app_dict["main"], main_commands_dir)

        orm_commands_dir = pkg_resources.files(framefox.terminal.commands.orm)
        self.load_commands_for_an_app(app_dict["orm"], orm_commands_dir, "orm")

        orm_database_commands_dir = pkg_resources.files(
            framefox.terminal.commands.orm.database
        )
        self.load_commands_for_an_app(
            app_dict["orm database"], orm_database_commands_dir, "database", "orm"
        )

        server_commands_dir = pkg_resources.files(framefox.terminal.commands.server)
        self.load_commands_for_an_app(app_dict["server"], server_commands_dir, "server")

        create_commands_dir = pkg_resources.files(framefox.terminal.commands.create)
        self.load_commands_for_an_app(app_dict["create"], create_commands_dir, "create")
        debug_commands_dir = pkg_resources.files(framefox.terminal.commands.debug)
        self.load_commands_for_an_app(app_dict["debug"], debug_commands_dir, "debug")
        cache_commands_dir = pkg_resources.files(framefox.terminal.commands.cache)
        self.load_commands_for_an_app(app_dict["cache"], cache_commands_dir, "cache")
        fixtures_commands_dir = pkg_resources.files(framefox.terminal.commands.fixtures)
        self.load_commands_for_an_app(
            app_dict["fixtures"], fixtures_commands_dir, "fixtures"
        )

    def load_commands_for_an_app(
        self, app: typer.Typer, commands_dir, dir=None, parent_dir=None
    ):
        """
        Load commands for a specific app.
        """
        to_ignore = [
            "abstract_command.py",
            "unsupported_command.py",
        ]
        for filename in self.custom_sort(os.listdir(commands_dir)):
            if filename.endswith("_command.py") and filename not in to_ignore:
                if not self.project_init and (
                    filename == "init_command.py" or filename == "check_command.py"
                ):
                    self.load_unique_command(app, filename, dir, parent_dir)
                elif (
                    self.project_init
                    and filename != "init_command.py"
                    and filename != "check_command.py"
                ):
                    self.load_unique_command(app, filename, dir, parent_dir)

    def load_unique_command(
        self, app: typer.Typer, filename: str, dir: str = None, parent_dir: str = None
    ):
        module_name = filename[:-3]
        if dir:
            if parent_dir:
                module = __import__(
                    f"framefox.terminal.commands.{parent_dir}.{dir}.{
                        module_name}",
                    fromlist=[module_name],
                )
            else:
                module = __import__(
                    f"framefox.terminal.commands.{dir}.{
                        module_name}",
                    fromlist=[module_name],
                )
        else:
            module = __import__(
                f"framefox.terminal.commands.{
                    module_name}",
                fromlist=[module_name],
            )
        class_name = "".join(word.capitalize() for word in module_name.split("_"))
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
            base_name = filename[:-11]
            for index, prefix in enumerate(self.priority_list):
                if base_name.startswith(prefix):
                    return (index, base_name)
            return (len(self.priority_list), base_name)

        return sorted(command_files, key=sort_key)
