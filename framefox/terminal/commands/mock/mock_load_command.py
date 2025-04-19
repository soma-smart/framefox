import importlib
import os

from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.input_manager import InputManager
from framefox.terminal.common.printer import Printer

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class MockLoadCommand(AbstractCommand):
    def execute(self):
        """
        Load all mocks found in the mocks directory.
        """
        mocks_dir = os.path.join("src", "mocks")
        if not os.path.exists(mocks_dir):
            Printer().print_msg(
                f"mocks directory not found: {mocks_dir}",
                theme="error",
            )
            return

        mock_files = [f for f in os.listdir(mocks_dir) if f.endswith("_mock.py")]

        if not mock_files:
            Printer().print_msg(
                "No mock files found in the mocks directory.",
                theme="error",
            )
            return
        Printer().print_msg(
            f"Found {len(mock_files)} mock(s): {', '.join(mock_files)}",
            theme="bold_normal",
            linebefore=True,
        )
        confirm = InputManager().wait_input(
            "Are you sure you want to load all these mocks?",
            default="no",
            choices=["yes", "no"],
        )

        if confirm.lower() != "yes":
            Printer().print_msg("Operation cancelled.", theme="error")
            return

        for mock_file in mock_files:
            mock_name = mock_file.replace("_mock.py", "")
            try:

                module_name = f"src.mocks.{mock_name}_mock"
                mock_module = importlib.import_module(module_name)

                mock_class_name = f"{mock_name.capitalize()}Mock"
                mock_class = getattr(mock_module, mock_class_name)

                mock_class.load()
                Printer().print_msg(
                    f"mock '{mock_file}' loaded successfully.",
                    theme="success",
                )
            except Exception as e:
                Printer().print_msg(
                    f"Error loading mock '{mock_file}': {str(e)}",
                    theme="error",
                )
