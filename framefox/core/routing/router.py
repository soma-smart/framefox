import importlib
import inspect
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from framefox.core.di.service_container import ServiceContainer
from framefox.core.templates.template_renderer import TemplateRenderer


class Router:
    _routes = {}

    def __init__(self, app: FastAPI):
        self.app = app
        self.container = ServiceContainer()
        self.settings = self.container.get_by_name("Settings")

    def _get_module_name(self, module_path: str) -> str:
        """Convert file path to module name."""
        path = Path(module_path)
        src_dir = Path.cwd() / "src"
        relative_path = path.relative_to(src_dir).with_suffix("")
        return ".".join(["src"] + list(relative_path.parts))

    def url_path_for(self, name: str, **params) -> str:
        """Generate URL for named route"""
        if name in self._routes:
            route_path = self._routes[name]

            for key, value in params.items():
                route_path = route_path.replace(f"{{{key}}}", str(value))
            return route_path
        return "#"

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

            async def default_route():
                template_renderer = self.container.get(TemplateRenderer)
                html_content = template_renderer.render("default.html", {})
                return HTMLResponse(content=html_content)

            self.app.add_api_route(
                "/", default_route, name="default_route", methods=["GET"]
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
                Router._routes[route["name"]] = route["path"]
                controller_instance.router.add_api_route(
                    path=route["path"],
                    endpoint=method,
                    name=route["name"],
                    methods=route["methods"],
                )
