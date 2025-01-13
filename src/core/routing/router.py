import importlib
<<<<<<< Updated upstream:src/core/routing/router.py
<<<<<<< Updated upstream:src/core/routing/router.py

from pathlib import Path
from fastapi import FastAPI
from src.core.controller.abstract_controller import AbstractController
import inspect
=======
=======
>>>>>>> Stashed changes:framefox/core/routing/router.py
from typing import Annotated
from pathlib import Path
from fastapi import FastAPI
import inspect
from injectable import autowired, Autowired
>>>>>>> Stashed changes:framefox/core/routing/router.py

from framefox.core.controller.abstract_controller import AbstractController
from framefox.core.config.settings import Settings

from framefox.core.controller.abstract_controller import AbstractController
from framefox.core.config.settings import Settings


class Router:
    def __init__(self, app: FastAPI):
        self.app = app

    def register_controllers(self):
        """
        Registers all controller classes found in the controllers directory with the FastAPI application.

        This method searches for all Python files in the 'controllers' directory, imports them, and registers
        any classes that are subclasses of `AbstractController`. Each controller's routes are then included
        in the FastAPI application.

        Args:
            app (FastAPI): The FastAPI application instance to register the controllers with.

        Raises:
            FileNotFoundError: If the 'controllers' directory does not exist.
        """
        controllers_folder = "controllers"

        controllers_path = (
            Path(__file__).resolve().parent.parent.parent / controllers_folder
        )
        if not controllers_path.exists():
            raise FileNotFoundError(
                f"Le dossier des contrôleurs '{
                    controllers_folder}' n'existe pas."
            )

        for file in controllers_path.glob("*.py"):
            if file.name == "__init__.py":
                continue
            module_name = f"src.controllers.{file.stem}"
            module = importlib.import_module(module_name)

            for attr_name in dir(module):
                controller_class = getattr(module, attr_name)
                if inspect.isclass(controller_class) and issubclass(
                    controller_class, AbstractController
                ):
                    controller_instance = controller_class()
                    Router._register_routes(controller_instance)
                    self.app.include_router(controller_instance.router)

    @staticmethod
    def _register_routes(controller_instance):
        """
        Iterates through all the methods of the controller and registers those decorated with @Route.
        """
        for name, method in inspect.getmembers(
            controller_instance, predicate=inspect.ismethod
        ):
            if hasattr(method, "route_info"):
                route = method.route_info
                controller_instance.router.add_api_route(
                    path=route["path"],
                    endpoint=method,
                    name=route["name"],
                    methods=route["methods"],
                )
