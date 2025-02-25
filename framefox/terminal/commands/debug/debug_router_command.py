import os
import sys

from rich.console import Console
from rich.table import Table

from framefox.core.kernel import Kernel
from framefox.terminal.commands.abstract_command import AbstractCommand

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class DebugRouterCommand(AbstractCommand):
    def __init__(self):
        super().__init__("router")

        current_dir = os.getcwd()
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)

        kernel = Kernel()
        self.app = kernel.app

    def execute(self):
        """
        Print the list of routes
        """
        console = Console()
        print("")
        table = Table(show_header=True, header_style="bold orange1")
        table.add_column("Path", style="bold orange3", no_wrap=True)
        table.add_column("Route name", style="white")
        table.add_column("HTTP Methods", style="white")

        unique_routes = {}
        for route in self.app.routes:
            route_key = f"{route.path}:{getattr(route, 'name', '')}"
            if route_key not in unique_routes and route_key != "/static:static":
                unique_routes[route_key] = route

        sorted_routes = sorted(unique_routes.values(), key=lambda x: x.path)

        for route in sorted_routes:
            methods = ", ".join(route.methods) if hasattr(
                route, "methods") else "GET"
            name = route.name if hasattr(route, "name") else ""
            table.add_row(route.path, name, methods)

        console.print(table)
        print("")
