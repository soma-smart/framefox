import os
import inspect
import importlib
from pathlib import Path
from fastapi import FastAPI
from fastapi.routing import APIRouter
from fastapi.responses import HTMLResponse
from framefox.core.config.settings import Settings
from framefox.core.di.service_container import ServiceContainer
from framefox.core.templates.template_renderer import TemplateRenderer


class Router:
    def __init__(self, app: FastAPI):
        self.app = app
        self.container = ServiceContainer()
        self.settings = self.container.get(Settings)

    def _get_module_name(self, module_path: str) -> str:
        """Convert file path to module name."""
        path = Path(module_path)
        src_dir = Path.cwd() / "src"
        relative_path = path.relative_to(src_dir).with_suffix("")
        return ".".join(["src"] + list(relative_path.parts))

    def register_controllers(self):
        controllers_path = os.path.join(os.getcwd(), "src", "controllers")
        for root, _, files in os.walk(controllers_path):
            for file in files:
                if file.endswith(".py"):
                    module_path = os.path.join(root, file)
                    module_name = self._get_module_name(module_path)
                try:
                    module = importlib.import_module(module_name)
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (
                            inspect.isclass(attr)
                            and attr.__module__ == module.__name__
                            and not attr.__name__.startswith("_")
                        ):
                            controller_instance = self.container.get(attr)
                            if controller_instance:
                                router = APIRouter()
                                setattr(controller_instance, "router", router)
                                self._register_routes(controller_instance)
                                self.app.include_router(router)
                except Exception as e:
                    print(f"Error loading controller {module_name}: {e}")

        if not any(route.path == "/" for route in self.app.routes):

            async def default_root():
                template_renderer = self.container.get(TemplateRenderer)
                html_content = template_renderer.render("default.html", {})
                return HTMLResponse(content=html_content)

            self.app.add_api_route(
                "/", default_root, name="default_root", methods=["GET"]
            )

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
