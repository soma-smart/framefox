# app/core/router.py
import importlib
import os
from src.core.abstract_controller import AbstractController


class Router:
    """Classe pour gérer les routes de l'application."""

    def __init__(self, app, controllers_folder="src.controllers"):
        self.app = app
        self.controllers_folder = controllers_folder

    def register_controllers(self):
        """Charge et enregistre dynamiquement tous les contrôleurs."""
        controllers_path = self.controllers_folder.replace(".", "/")
        for filename in os.listdir(controllers_path):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = f"{self.controllers_folder}.{filename[:-3]}"
                module = importlib.import_module(module_name)

                for attr_name in dir(module):
                    controller_class = getattr(module, attr_name)
                    if isinstance(controller_class, type) and issubclass(controller_class, AbstractController):
                        controller_instance = controller_class()
                        for route in controller_instance.routes:
                            self.app.add_url_rule(
                                route["path"],
                                endpoint=route["endpoint"],
                                view_func=route["view_func"],
                                methods=route["methods"],
                            )
