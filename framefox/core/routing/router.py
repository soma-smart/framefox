import importlib
import inspect
import logging
import os
from pathlib import Path
from typing import Dict, List, Type

from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.routing import APIRouter

from framefox.core.controller.controller_resolver import ControllerResolver
from framefox.core.debug.exception.controller_exception import ControllerException
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
    """
    Dynamic router for registering and managing FastAPI controllers
    with support for lazy loading and framework-specific controllers
    """

    _routes: Dict[str, str] = {}
    _instances: Dict[int, "Router"] = {}

    def __new__(cls, app=None):
        """Singleton pattern per process to avoid multiple router instances"""
        process_id = os.getpid()
        if process_id not in cls._instances:
            cls._instances[process_id] = super(Router, cls).__new__(cls)
            cls._instances[process_id]._initialized = False
        return cls._instances[process_id]

    def __init__(self, app=None):
        """Initialize the router with required dependencies"""
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.app = app
        self.container = ServiceContainer()
        self.controller_resolver = ControllerResolver()
        self.settings = self.container.get_by_name("Settings")
        self.logger = logging.getLogger("ROUTER")
        self._initialized = True

    def register_controllers(self):
        """Register all controllers dynamically with proper error handling"""
        try:
            self._setup_handlers()

            if self.settings.app_env == "dev":
                self._register_framework_controllers()

            self._register_user_controllers()

            self._register_default_route()

            self.logger.debug("Controller registration completed successfully")

        except Exception as e:
            self.logger.error(f"Failed to register controllers: {e}")
            raise

    def _setup_handlers(self):
        """Configure base HTTP handlers and middleware"""
        try:
            self._setup_trailing_slash_middleware()
            self._setup_404_handler()
            self.logger.debug("Base handlers configured successfully")
        except Exception as e:
            self.logger.error(f"Failed to setup handlers: {e}")
            raise

    def _setup_trailing_slash_middleware(self):
        """Configure middleware to handle trailing slashes"""

        @self.app.middleware("http")
        async def trailing_slash_handler(request: Request, call_next):
            path = request.url.path

            # Skip processing for static files, profiler routes, files with extensions, root, or paths without trailing slash
            if path.startswith(("/static/", "/_profiler/")) or "." in path.split("/")[-1] or len(path) <= 1 or not path.endswith("/"):
                return await call_next(request)

            # Redirect to URL without trailing slash
            new_url = str(request.url.replace(path=path.rstrip("/")))
            return RedirectResponse(url=new_url, status_code=301)

    def _setup_404_handler(self):
        """Configure custom 404 error handler"""

        @self.app.exception_handler(404)
        async def custom_404_handler(request: Request, exc: HTTPException):
            if exc.status_code != 404:
                raise exc

            # Handle JSON requests
            accept_header = request.headers.get("accept", "")
            if "application/json" in accept_header:
                return JSONResponse(content={"error": "Not Found", "status_code": 404}, status_code=404)

            # Handle HTML requests
            try:
                template_renderer = self.container.get(TemplateRenderer)
                html_content = template_renderer.render("404.html", {"request": request, "error": "Page not found"})
                return HTMLResponse(content=html_content, status_code=404)
            except Exception as e:
                self.logger.error(f"Failed to render 404 template: {e}")
                return HTMLResponse(content="<h1>404 - Page Not Found</h1>", status_code=404)

    def _register_framework_controllers(self):
        """Register framework-specific controllers (profiler, etc.)"""
        framework_controllers = ["framefox.core.debug.profiler.profiler_controller.ProfilerController"]

        registered_count = 0
        for controller_path in framework_controllers:
            try:
                controller_class = self._import_class(controller_path)
                instance = controller_class()
                self._register_controller_routes(instance, direct=True)
                registered_count += 1
                self.logger.debug(f"Registered framework controller: {controller_class.__name__}")
            except Exception as e:
                self.logger.debug(f"Failed to register framework controller {controller_path}: {e}")

        if registered_count > 0:
            self.logger.debug(f"Registered {registered_count} framework controllers")

    def _register_user_controllers(self):
        controllers_path = Path("src/controller")
        if not controllers_path.exists():
            self.logger.debug("No user controllers directory found")
            return

        registered_count = 0
        for controller_file in controllers_path.rglob("*.py"):
            if controller_file.name == "__init__.py":
                continue

            try:
                module_name = self._get_module_name(controller_file)
                controller_classes = self._discover_controller_classes(module_name)

                for controller_class in controller_classes:
                    controller_name = controller_class.__name__.replace("Controller", "").lower()

                    def create_lazy_factory(name: str):
                        return lambda: self.controller_resolver.resolve_controller(name)

                    lazy_factory = create_lazy_factory(controller_name)
                    self._register_controller_routes(controller_class, lazy_factory=lazy_factory)
                    registered_count += 1
                    self.logger.debug(f"Registered lazy controller: {controller_class.__name__}")

            except Exception as e:
                self.logger.error(f"Failed to register controller {controller_file}: {e}")
                continue

    def _register_controller_routes(self, controller, lazy_factory=None, direct=False):
        """Register routes for a controller (instance or class)"""
        try:
            if direct and hasattr(controller, "__class__"):
                self._register_direct_controller(controller)
            elif lazy_factory:
                self._register_lazy_controller(controller, lazy_factory)
            else:
                self.logger.warning(f"Invalid controller registration parameters for {controller}")
        except Exception as e:
            controller_name = getattr(controller, "__name__", "unknown")
            self.logger.error(f"Failed to register routes for controller {controller_name}: {e}")

    def _register_direct_controller(self, controller_instance):
        """Register routes for a direct controller instance"""
        controller_class = controller_instance.__class__
        router = APIRouter()
        setattr(controller_instance, "router", router)

        route_count = 0
        for method_name, method in inspect.getmembers(controller_instance, predicate=inspect.ismethod):
            if self._process_method_route(method, method.__func__, controller_class, router, method):
                route_count += 1

        self.app.include_router(router)
        self.logger.debug(f"Registered {route_count} routes for direct controller {controller_class.__name__}")

    def _register_lazy_controller(self, controller_class, lazy_factory):
        """Register routes for a lazy-loaded controller"""
        router = APIRouter()
        route_count = 0

        for method_name, method in inspect.getmembers(controller_class, predicate=inspect.isfunction):
            endpoint = self._create_lazy_endpoint(method_name, method, lazy_factory)
            if self._process_method_route(method, method, controller_class, router, endpoint):
                route_count += 1

        self.app.include_router(router)
        self.logger.debug(f"Registered {route_count} routes for lazy controller {controller_class.__name__}")

    def _process_method_route(self, method, method_func, controller_class, router, endpoint) -> bool:
        """Process a method to create routes, returns True if route was created"""
        if hasattr(method_func, "route_info") and not method_func.__name__.startswith("_"):
            return self._process_route_info(method_func, controller_class, router, endpoint)

        if hasattr(method_func, "webhook_info") and not method_func.__name__.startswith("_"):
            return self._process_webhook_info(method_func, controller_class, router, endpoint)

        return False

    def _process_route_info(self, method_func, controller_class, router, endpoint) -> bool:
        """Process regular route info"""
        try:
            route = method_func.route_info
            Router._routes[route["name"]] = route["path"]

            controller_tag = controller_class.__name__.replace("Controller", "").title()
            route_tags = route.get("tags", []) or [controller_tag]

            for http_method in route["methods"]:
                router.add_api_route(
                    path=route["path"],
                    endpoint=endpoint,
                    name=f"{route['name']}_{http_method.lower()}",
                    methods=[http_method],
                    tags=route_tags,
                    response_model=route.get("response_model"),
                    operation_id=route.get("operation_ids", {}).get(http_method),
                )

            return True
        except Exception as e:
            self.logger.error(f"Failed to process route for method {method_func.__name__}: {e}")
            return False

    def _process_webhook_info(self, method_func, controller_class, router, endpoint) -> bool:
        """Process webhook info"""
        try:
            webhook = method_func.webhook_info
            Router._routes[webhook["name"]] = webhook["path"]

            controller_tag = controller_class.__name__.replace("Controller", "").title()
            webhook_tags = [f"{controller_tag} Webhooks"]

            for http_method in webhook["methods"]:
                router.add_api_route(
                    path=webhook["path"],
                    endpoint=endpoint,
                    name=f"{webhook['name']}_{http_method.lower()}",
                    methods=[http_method],
                    tags=webhook_tags,
                    operation_id=f"{webhook['name']}_{http_method.lower()}_webhook",
                )

            return True
        except Exception as e:
            self.logger.error(f"Failed to process webhook for method {method_func.__name__}: {e}")
            return False

    def _create_lazy_endpoint(self, method_name: str, original_method, lazy_factory):
        """Create a lazy endpoint with clean error handling"""
        try:
            sig = inspect.signature(original_method)
            params = [param.replace(annotation=param.annotation) for name, param in sig.parameters.items() if name != "self"]
            new_sig = sig.replace(parameters=params)

            async def lazy_endpoint(*args, **kwargs):
                try:
                    controller_instance = lazy_factory()
                    method_to_call = getattr(controller_instance, method_name)

                    result = await method_to_call(*args, **kwargs)

                    if hasattr(controller_instance, "_last_rendered_template"):

                        request = None
                        for arg in args:
                            if hasattr(arg, "scope") and "type" in arg.scope:
                                request = arg
                                break

                        if request:
                            request.state.template = controller_instance._last_rendered_template
                            request.state.controller_instance = controller_instance

                    return result
                except Exception:
                    raise

            lazy_endpoint.__signature__ = new_sig
            lazy_endpoint.__name__ = f"lazy_{method_name}"

            if hasattr(original_method, "route_info"):
                lazy_endpoint.route_info = original_method.route_info

            lazy_endpoint.__module__ = original_method.__module__
            lazy_endpoint.__qualname__ = original_method.__qualname__
            lazy_endpoint.__original_method__ = original_method
            lazy_endpoint.__controller_name__ = lazy_factory().__class__.__name__ if callable(lazy_factory) else "Unknown"
            lazy_endpoint.__method_name__ = method_name

            return lazy_endpoint

        except Exception as e:
            raise

    def _discover_controller_classes(self, module_name: str) -> List[Type]:
        try:
            module = importlib.import_module(module_name)
            controllers = []
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    hasattr(attr, "__module__")
                    and inspect.isclass(attr)
                    and attr.__module__ == module_name
                    and attr_name.endswith("Controller")
                    and not attr_name.startswith("_")
                ):
                    controllers.append(attr)
            return controllers
        except Exception as e:
            self.logger.error(f"Failed to discover controllers in {module_name}: {e}")
            return []

    def _register_default_route(self):
        """Register default development route if no root route exists"""
        if any(route.path == "/" for route in self.app.routes) or self.settings.app_env != "dev":
            return

        try:

            async def default_route():
                try:
                    template_renderer = self.container.get(TemplateRenderer)
                    html_content = template_renderer.render("default.html", {})
                    return HTMLResponse(content=html_content, status_code=200)
                except Exception as e:
                    self.logger.error(f"Failed to render default template: {e}")
                    return HTMLResponse(content="<h1>Welcome to Framefox</h1>", status_code=200)

            self.app.add_api_route("/", default_route, name="default_route", methods=["GET"])
            self.logger.debug("Registered default development route")
        except Exception as e:
            self.logger.error(f"Failed to register default route: {e}")

    def _get_module_name(self, file_path: Path) -> str:
        """Convert a file path to a module name"""
        try:
            relative_path = file_path.relative_to(Path("src")).with_suffix("")
            return f"src.{relative_path.as_posix().replace('/', '.')}"
        except Exception as e:
            self.logger.error(f"Failed to get module name for {file_path}: {e}")
            raise

    def _import_class(self, class_path: str) -> Type:
        """Import a class from its full path"""
        try:
            module_path, class_name = class_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            return getattr(module, class_name)
        except Exception as e:
            self.logger.error(f"Failed to import class {class_path}: {e}")
            raise

    def url_path_for(self, name: str, **params) -> str:
        """Generate URL for a named route with parameters"""
        if name not in self._routes:
            self.logger.warning(f"Route '{name}' not found in registered routes")
            return "#"

        try:
            route_path = self._routes[name]
            for key, value in params.items():
                route_path = route_path.replace(f"{{{key}}}", str(value))
            return route_path
        except Exception as e:
            self.logger.error(f"Failed to generate URL for route '{name}': {e}")
            return "#"

    def get_registered_routes(self) -> Dict[str, str]:
        """Get a copy of all registered routes"""
        return self._routes.copy()

    def route_exists(self, name: str) -> bool:
        """Check if a route exists"""
        return name in self._routes
