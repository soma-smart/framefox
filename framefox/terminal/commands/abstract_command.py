from framefox.core.config.settings import Settings
from framefox.core.debug.exception.settings_exception import SettingsException
from framefox.terminal.common.printer import Printer

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen & LEUROND Raphael
Github: https://github.com/RayenBou
Github: https://github.com/Vasulvius
"""


class AbstractCommand:
    """
    Abstract base class for all commands.

    """

    def __init__(self, name=None):
        """
        Initializes the command

        Args:
            name: The command name (used for namespace:name convention)
        """
        self.name = name or self.__class__.__name__.replace("Command", "").lower()
        self.printer = Printer()
        self._container = None

    def execute(self, *args, **kwargs):
        """
        Executes the command. Must be implemented by subclasses.

        Args:
            *args: Positional arguments
            **kwargs: Named arguments

        Returns:
            int: Return code (0 = success, other = failure)
        """
        raise NotImplementedError("Subclasses must implement this method")

    def get_settings(self):
        """
        Returns the application settings.

        Returns:
            Settings: The application settings object.
        """
        try:
            return Settings()
        except SettingsException as e:
            from framefox.core.debug.handler.startup_error_handler import (
                StartupErrorHandler,
            )

            StartupErrorHandler.handle_configuration_error(e)
        except Exception as e:
            print(f"\n🚫 \033[91mConfiguration Error:\033[0m {e}")
            import sys

            sys.exit(1)
