import importlib
import inspect
import logging
import os
from pathlib import Path

from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
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
    _instances = {}
    _registered_controllers = {}

    def __new__(cls, app=None):
        process_id = os.getpid()

        if process_id not in cls._instances:
            cls._instances[process_id] = super(Router, cls).__new__(cls)
            cls._instances[process_id]._initialized = False
            cls._registered_controllers[process_id] = set()

        return cls._instances[process_id]

    def __init__(self, app=None):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.process_id = os.getpid()
        self.logger = logging.getLogger("ROUTER")

        if app:
            self.app = app
            self.container = ServiceContainer()
            self.settings = self.container.get_by_name("Settings")
            self._initialized = True

    def register_controllers(self):
        self._register_handlers()
        controllers_path = os.path.join(os.getcwd(), "src", "controller")

        process_controllers = self._registered_controllers.get(self.process_id, set())

        if process_controllers:
            return

        registered_controller_classes = set()

        for root, _, files in os.walk(controllers_path):
            for file in files:
                if file.endswith(".py"):
                    module_path = os.path.join(root, file)
                    module_name = self._get_module_name(module_path)

                    if module_name in process_controllers:
                        continue

                    try:
                        module = importlib.import_module(module_name)

                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)

                            if inspect.isclass(attr) and attr.__module__ == module.__name__ and not attr.__name__.startswith("_"):

                                controller_key = f"{attr.__module__}.{attr.__name__}"

                                if controller_key in registered_controller_classes:
                                    continue

                                controller_instance = self.container.get(attr)
                                if controller_instance:
                                    router = APIRouter()
                                    setattr(controller_instance, "router", router)
                                    self._register_routes(controller_instance)
                                    self.app.include_router(router)

                                    registered_controller_classes.add(controller_key)

                        process_controllers.add(module_name)
                        self._registered_controllers[self.process_id] = process_controllers

                    except Exception as e:
                        self.logger.error(f"Failed to register controller {module_name}: {e}")

        self._register_default_route()

    @staticmethod
    def _register_routes(controller_instance):
        for name, method in inspect.getmembers(controller_instance, predicate=inspect.ismethod):
            if hasattr(method, "route_info"):
                route = method.route_info
                Router._routes[route["name"]] = route["path"]

                operation_ids = route.get("operation_ids", {})

                for http_method in route["methods"]:
                    route_kwargs = {
                        "path": route["path"],
                        "endpoint": method,
                        "name": f"{route['name']}_{http_method.lower()}",
                        "methods": [http_method],
                        "response_model": None,
                    }

                    if http_method in operation_ids:
                        route_kwargs["operation_id"] = operation_ids[http_method]

                    if route.get("response_model") is not None:
                        route_kwargs["response_model"] = route["response_model"]

                    controller_instance.router.add_api_route(**route_kwargs)

    def _register_default_route(self):
        if not any(route.path == "/" for route in self.app.routes) and self.settings.app_env == "dev":

            async def default_route():
                template_renderer = self.container.get(TemplateRenderer)
                html_content = template_renderer.render("default.html", {})
                return HTMLResponse(content=html_content, status_code=404)

            self.app.add_api_route("/", default_route, name="default_route", methods=["GET"])

    def _get_module_name(self, module_path: str) -> str:
        path = Path(module_path)
        src_dir = Path.cwd() / "src"
        relative_path = path.relative_to(src_dir).with_suffix("")
        return ".".join(["src"] + list(relative_path.parts))

    def url_path_for(self, name: str, **params) -> str:
        if name in self._routes:
            route_path = self._routes[name]
            for key, value in params.items():
                route_path = route_path.replace(f"{{{key}}}", str(value))
            return route_path
        return "#"

    def _register_handlers(self):
        @self.app.middleware("http")
        async def trailing_slash_handler(request: Request, call_next):
            path = request.url.path

            if path.startswith("/static/") or path.startswith("/_profiler/") or "." in path.split("/")[-1]:
                return await call_next(request)

            if len(path) > 1 and path.endswith("/"):
                new_path = path.rstrip("/")
                new_url = str(request.url.replace(path=new_path))
                return RedirectResponse(url=new_url, status_code=301)

            return await call_next(request)

        @self.app.exception_handler(404)
        async def custom_404_handler(request: Request, exc: HTTPException):
            if exc.status_code == 404:
                accept_header = request.headers.get("accept", "")

                if "application/json" in accept_header or "text/html" not in accept_header:
                    from fastapi.responses import JSONResponse

                    return JSONResponse(content={"error": "Not Found", "status_code": 404}, status_code=404)
                else:
                    template_renderer = self.container.get(TemplateRenderer)
                    html_content = template_renderer.render("404.html", {"request": request, "error": "Page not found"})
                    return HTMLResponse(content=html_content, status_code=404)
            raise exc

    def _register_profiler_routes(self):
        try:
            profiler_controller = self.container.get_by_name("ProfilerController")
            router = APIRouter(prefix="")
            setattr(profiler_controller, "router", router)
            self._register_routes(profiler_controller)
            self.app.include_router(router)
        except Exception:
            pass
