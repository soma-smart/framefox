from framefox.terminal.common.printer import Printer
from framefox.core.di.service_container import ServiceContainer
from framefox.core.config.settings import Settings
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

    def get_container(self):
        """Gets the service container (lazy loading)"""
        if self._container is None:
            self._container = ServiceContainer()
        return self._container

    def get_settings(self):
        """Gets the application settings"""
        return Settings()