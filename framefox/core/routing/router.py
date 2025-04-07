import importlib
import inspect
import os
from pathlib import Path

from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter

from framefox.core.di.service_container import ServiceContainer
from framefox.core.templates.template_renderer import TemplateRenderer

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class Router:
    _routes = {}
    _instance = None

    def __new__(cls, app=None):
        if cls._instance is None:
            cls._instance = super(Router, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, app=None):
        if hasattr(self, "_initialized") and self._initialized:
            return

        if app:
            self.app = app
            self.container = ServiceContainer()
            self.settings = self.container.get_by_name("Settings")
            self._initialized = True

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

    def register_exception_handlers(self):
        """Register custom exception handlers"""

        @self.app.exception_handler(404)
        async def custom_404_handler(request: Request, exc: HTTPException):
            if exc.status_code == 404:
                template_renderer = self.container.get(TemplateRenderer)
                html_content = template_renderer.render(
                    "404.html", {"request": request, "error": "Page non trouvée"}
                )
                return HTMLResponse(content=html_content, status_code=404)
            raise exc

    def register_controllers(self):
        self.register_exception_handlers()
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

        if (
            not any(route.path == "/" for route in self.app.routes)
            and self.settings.app_env == "dev"
        ):

            async def default_route():
                template_renderer = self.container.get(TemplateRenderer)
                html_content = template_renderer.render("default.html", {})
                return HTMLResponse(content=html_content, status_code=404)

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
