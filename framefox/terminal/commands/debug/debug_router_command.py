import os
import sys

from framefox.application import Application
from framefox.terminal.commands.abstract_command import AbstractCommand
from rich.console import Console
from rich.table import Table


class DebugRouterCommand(AbstractCommand):
    """
    A command to display and debug router information in the Framefox Framework.
    This class provides functionality to list all registered routes with their paths,
    names, and HTTP methods.

    Attributes:
        app: The FastAPI application instance containing the routes.
    """

    def __init__(self):
        super().__init__("router")
        self._app = None

    @property
    def app(self):
        """Lazy loading de l'application - ne charge que quand nécessaire"""
        if self._app is None:
            current_dir = os.getcwd()
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)

            application = Application()
            kernel = application.boot_web()
            self._app = kernel.app
        return self._app

    def execute(self):
        """
        Display and debug router information.\n
        This method retrieves all routes from the FastAPI application,\n
        filters out certain routes, and prints a formatted table with the\n
        route paths, names, and HTTP methods.\n
        """
        console = Console()
        print("")
        table = Table(show_header=True, header_style="bold orange1")
        table.add_column("Path", style="bold orange3", no_wrap=True)
        table.add_column("Route name", style="white")
        table.add_column("HTTP Methods", style="white")

        routes_to_exclude = [
            "public_assets",
            "default_route",
            "swagger_ui_html",
            "swagger_ui_redirect",
            "openapi",
            "redoc_html",
            "static",
        ]

        unique_routes = {}
        for route in self.app.routes:
            route_name = getattr(route, "name", "")
            route_key = f"{route.path}:{route_name}"

            if route_name not in routes_to_exclude and route_key not in unique_routes:
                unique_routes[route_key] = route

        sorted_routes = sorted(unique_routes.values(), key=lambda x: x.path)

        for route in sorted_routes:
            methods = ", ".join(route.methods) if hasattr(route, "methods") else "GET"
            name = route.name if hasattr(route, "name") else ""
            table.add_row(route.path, name, methods)

        console.print(table)
        print("")
