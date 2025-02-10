import importlib
import os
from typing import Optional

from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.input_manager import InputManager
from framefox.terminal.common.printer import Printer


class FixturesLoadCommand(AbstractCommand):
    def __init__(self):
        super().__init__("load")

    def execute(self):
        """
        Load all fixtures found in the fixtures directory.
        """
        fixtures_dir = os.path.join("src", "fixtures")
        if not os.path.exists(fixtures_dir):
            Printer().print_msg(
                f"Fixtures directory not found: {fixtures_dir}",
                theme="error",
            )
            return

        fixture_files = [
            f for f in os.listdir(fixtures_dir) if f.endswith("_fixture.py")
        ]

        if not fixture_files:
            Printer().print_msg(
                "No fixture files found in the fixtures directory.",
                theme="error",
            )
            return
        Printer().print_msg(
            f"Found {len(fixture_files)} fixture(s): {', '.join(fixture_files)}",
            theme="bold_normal",
            linebefore=True,
        )
        confirm = InputManager().wait_input(
            "Are you sure you want to load all these fixtures?",
            default="no",
            choices=["yes", "no"],
        )

        if confirm.lower() != "yes":
            Printer().print_msg("Operation cancelled.", theme="error")
            return

        for fixture_file in fixture_files:
            fixture_name = fixture_file.replace("_fixture.py", "")
            try:

                module_name = f"src.fixtures.{fixture_name}_fixture"
                fixture_module = importlib.import_module(module_name)

                fixture_class_name = f"{fixture_name.capitalize()}Fixture"
                fixture_class = getattr(fixture_module, fixture_class_name)

                fixture_class.load()
                Printer().print_msg(
                    f"Fixture '{fixture_file}' loaded successfully.",
                    theme="success",
                )
            except Exception as e:
                Printer().print_msg(
                    f"Error loading fixture '{fixture_file}': {str(e)}",
                    theme="error",
                )
