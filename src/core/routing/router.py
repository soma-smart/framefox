import importlib
from pathlib import Path
from fastapi import FastAPI
from src.core.config.settings import Settings
from src.core.controller.abstract_controller import AbstractController


def register_controllers(app: FastAPI):
    settings = Settings()
    controllers_folder = "controllers"

    controllers_path = Path(__file__).resolve(
    ).parent.parent.parent / controllers_folder
    if not controllers_path.exists():
        raise FileNotFoundError(f"The controllers folder '{
                                controllers_folder}' does not exist.")

    for file in controllers_path.glob('*.py'):
        if file.name == "__init__.py":
            continue
        module_name = f"src.controllers.{file.stem}"
        module = importlib.import_module(module_name)

        for attr_name in dir(module):
            controller_class = getattr(module, attr_name)
            if isinstance(controller_class, type) and issubclass(controller_class, AbstractController):
                controller_instance = controller_class()
                app.include_router(controller_instance.router)
