import os
import sys
from pathlib import Path
from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.core.routing.router import Router
from framefox.core.kernel import Kernel
from rich.table import Table
from rich.console import Console


class DebugRouterCommand(AbstractCommand):
    def __init__(self):
        super().__init__("router")
        # Ajouter le répertoire courant au PYTHONPATH
        current_dir = os.getcwd()
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)

        kernel = Kernel()
        self.app = kernel.app
        # Ne plus créer de nouveau Router car déjà fait dans le Kernel
        # self.router = Router(self.app)

    def execute(self):
        """
        Print the list of routes
        """
        console = Console()
        print("")

        # Créer un tableau pour l'affichage
        table = Table(show_header=True, header_style="bold orange1")
        table.add_column("Path", style="bold orange3", no_wrap=True)
        table.add_column("Route name", style="white")
        table.add_column("HTTP Methods", style="white")

        # Utiliser un dictionnaire pour dédupliquer les routes
        unique_routes = {}
        for route in self.app.routes:
            route_key = f"{route.path}:{getattr(route, 'name', '')}"
            if route_key not in unique_routes:
                unique_routes[route_key] = route

        # Trier les routes uniques par path
        sorted_routes = sorted(unique_routes.values(), key=lambda x: x.path)

        # Ajouter chaque route unique
        for route in sorted_routes:
            methods = ", ".join(route.methods) if hasattr(
                route, "methods") else "GET"
            name = route.name if hasattr(route, "name") else ""
            table.add_row(route.path, name, methods)

        # Afficher le tableau
        console.print(table)
        print("")
