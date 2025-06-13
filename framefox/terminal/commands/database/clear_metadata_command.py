import importlib
import sys

from sqlalchemy.orm import clear_mappers
from sqlmodel import SQLModel

from framefox.terminal.commands.database.abstract_database_command import (
    AbstractDatabaseCommand,
)

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class ClearMetadataCommand(AbstractDatabaseCommand):
    def __init__(self):
        super().__init__("clear-metadata")

    def execute(self):
        """
        Cleans SQLAlchemy metadata and Python cache to resolve mapper issues.\n
        This command will clear the SQLAlchemy metadata and reload the necessary modules\n
        to ensure that the application can start fresh without any stale metadata.\n
        It is useful when you have made changes to your entity models and need to reset\n
        the SQLAlchemy registry to avoid issues with stale mappers or metadata.\n
        """
        try:
            self.printer.print_msg("Cleaning SQLAlchemy metadata...", theme="info")

            self.clear_sqlalchemy_registry()

            self.printer.print_msg("Metadata cleaned successfully", theme="success")
            self.printer.print_msg("Restart your application to apply the changes", theme="info")

        except Exception as e:
            self.printer.print_msg(
                f"Error while cleaning metadata: {str(e)}",
                theme="error",
            )

    def clear_sqlalchemy_registry(self):
        """Resets the SQLAlchemy registry"""
        try:

            clear_mappers()

            try:
                if hasattr(SQLModel, "metadata"):
                    SQLModel.metadata.clear()
                    self.printer.print_msg("SQLModel.metadata cleaned", theme="info")

                if hasattr(SQLModel, "__class__") and hasattr(SQLModel.__class__, "registry"):
                    SQLModel.__class__.registry.dispose()
                    self.printer.print_msg("SQLModel registry cleaned", theme="info")
            except Exception as inner_e:
                self.printer.print_msg(f"Partial cleaning of SQLModel: {str(inner_e)}", theme="warning")

            if "sqlmodel" in sys.modules:
                importlib.reload(sys.modules["sqlmodel"])
                self.printer.print_msg("SQLModel module reloaded", theme="info")

            modules_to_reload = [
                "framefox.core.orm.abstract_entity",
                "src.entity",
                "sqlalchemy.orm.mapper",
            ]

            for module_name in modules_to_reload:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])

            entity_modules = [m for m in sys.modules if m.startswith("src.entity.")]
            for module_name in entity_modules:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])

            self.printer.print_msg("SQLAlchemy registries reset", theme="info")

        except ImportError as e:
            self.printer.print_msg(f"Module not found: {str(e)}", theme="warning")

        except Exception as e:
            self.printer.print_msg(f"Error during reset: {str(e)}", theme="warning")
