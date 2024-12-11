
import importlib
from pathlib import Path
from src.core.controller.abstract_controller import AbstractController
from src.core.middleware.auth_middleware import AuthMiddleware
from src.core.config.settings import Settings


class Router:
    """
    Class to manage the application's routes.

    Attributes:
        app: The application instance to which routes will be added.
        controllers_folder (str): The folder where controller modules are located.
        settings (Settings): An instance of the Settings class to manage configuration.
        auth_middleware (AuthMiddleware or None): Middleware for authentication, if enabled.

    Methods:
        register_controllers():
            Dynamically load and register all controllers from the controllers folder.
            Raises:
                FileNotFoundError: If the controllers folder does not exist.
    """
    """Class to manage the application's routes."""

    def __init__(self, app, controllers_folder="controllers"):
        self.app = app
        self.controllers_folder = controllers_folder
        self.settings = Settings()

        # Initialize middleware if auth is enabled
        if self.settings.is_auth_enabled:
            self.auth_middleware = AuthMiddleware(
                self.settings.access_control
            )
        else:
            self.auth_middleware = None

    def register_controllers(self):

        controllers_path = Path(__file__).resolve(
        ).parent.parent.parent / self.controllers_folder
        if not controllers_path.exists():
            raise FileNotFoundError(f"The controllers folder '{
                                    self.controllers_folder}' does not exist.")

        for file in controllers_path.glob('*.py'):
            if file.name == "__init__.py":
                continue
            module_name = f"src.controllers.{file.stem}"
            module = importlib.import_module(module_name)

            for attr_name in dir(module):
                controller_class = getattr(module, attr_name)
                if isinstance(controller_class, type) and issubclass(controller_class, AbstractController):
                    controller_instance = controller_class()
                    for route in controller_instance.routes:
                        view_func = route["view_func"]

                        # Apply middleware if necessary
                        if self.auth_middleware:
                            view_func = self.auth_middleware(view_func)

                        self.app.add_url_rule(
                            route["path"],
                            endpoint=route["endpoint"],
                            view_func=view_func,
                            methods=route["methods"],
                        )
