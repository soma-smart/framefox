import importlib
import inspect
from pathlib import Path
from typing import get_type_hints

from rich import box
from rich.console import Console
from rich.table import Table

from framefox.terminal.commands.abstract_command import AbstractCommand

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class DebugRouterCommand(AbstractCommand):

    def __init__(self):
        super().__init__()

    def execute(self):
        """
        Command to display routing information with method parameters.
        This command scans user-defined controllers and framework controllers
        to extract routing information, including paths, HTTP methods, controller names,
        method names, and parameters with their types.
        """
        console = Console()
        routes_data = []
        self._scan_user_controllers(routes_data)
        self._scan_framework_controllers(routes_data)
        if not routes_data:
            console.print("❌ [red]No routes found[/red]")
            return
        self._display_routes_table(console, routes_data)

    def _scan_user_controllers(self, routes_data: list):
        controller_dir = Path.cwd() / "src" / "controller"
        if not controller_dir.exists():
            return
        for controller_file in controller_dir.rglob("*.py"):
            if controller_file.name == "__init__.py":
                continue
            try:
                rel_path = controller_file.relative_to(Path.cwd() / "src")
                module_name = f"src.{rel_path.with_suffix('').as_posix().replace('/', '.')}"
                self._scan_module_for_routes(module_name, routes_data)
            except Exception as e:
                print(f"⚠️  Error scanning {controller_file.name}: {e}")

    def _scan_framework_controllers(self, routes_data: list):
        framework_controllers = ["framefox.core.debug.profiler.profiler_controller"]
        for module_name in framework_controllers:
            try:
                self._scan_module_for_routes(module_name, routes_data)
            except Exception as e:
                print(f"⚠️  Error scanning framework controller {module_name}: {e}")

    def _scan_module_for_routes(self, module_name: str, routes_data: list):
        try:
            module = importlib.import_module(module_name)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if inspect.isclass(attr) and attr.__module__ == module_name and attr.__name__.endswith("Controller"):
                    controller_name = attr.__name__
                    for method_name, method in inspect.getmembers(attr, predicate=inspect.isfunction):
                        if hasattr(method, "route_info"):
                            route = method.route_info
                            path = route.get("path", "")
                            methods = route.get("methods", [])
                            method_params = self._analyze_method_parameters(method)
                            routes_data.append(
                                {
                                    "path": path,
                                    "http_methods": ", ".join(methods),
                                    "controller": controller_name,
                                    "method": method_name,
                                    "parameters": method_params,
                                }
                            )
        except Exception:
            pass

    def _analyze_method_parameters(self, method) -> str:
        try:
            signature = inspect.signature(method)
            try:
                type_hints = get_type_hints(method)
            except Exception:
                type_hints = {}
            params = []
            for param_name, param in signature.parameters.items():
                if param_name == "self":
                    continue
                param_str = param_name
                if param_name in type_hints:
                    type_name = self._get_type_name(type_hints[param_name])
                    param_str += f": {type_name}"
                elif param.annotation != inspect.Parameter.empty:
                    type_name = self._get_type_name(param.annotation)
                    param_str += f": {type_name}"
                if param.default != inspect.Parameter.empty:
                    param_str += f" = {repr(param.default)}"
                params.append(param_str)
            return "(" + ", ".join(params) + ")"
        except Exception as e:
            return f"(error: {e})"

    def _get_type_name(self, type_annotation) -> str:
        if hasattr(type_annotation, "__name__"):
            return type_annotation.__name__
        elif hasattr(type_annotation, "_name"):
            return type_annotation._name
        elif str(type_annotation).startswith("typing."):
            return str(type_annotation).replace("typing.", "")
        else:
            return str(type_annotation)

    def _display_routes_table(self, console: Console, routes_data: list):
        table = Table(
            show_header=True,
            header_style="bold orange3",
            show_lines=True,
            box=box.ROUNDED,
        )
        table.add_column("Path", style="cyan", no_wrap=True)
        table.add_column("HTTP", style="green")
        table.add_column("Controller", style="yellow")
        table.add_column("Method", style="white")
        table.add_column("Parameters", style="blue")
        routes_data.sort(key=lambda x: x["path"])
        for route in routes_data:
            path = route["path"]
            methods = route["http_methods"]
            controller = route["controller"].replace("Controller", "")
            method = route["method"]
            parameters = route["parameters"]
            table.add_row(path, methods, controller, method, parameters)
        console.print(table)

    def get_help_text(self) -> str:
        """
        Return the help text for this command.
        """
        return """
        Display routing information with method parameters.
        Usage: framefox debug router
        """
