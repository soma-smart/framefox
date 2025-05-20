import inspect
from rich.console import Console
from rich.table import Table
from framefox.core.di.service_container import ServiceContainer
from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.application import Application

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""

class DebugServiceCommand(AbstractCommand):
    """
    A command class for debugging and displaying service information in the Framefox Framework.
    
    This command provides detailed information about all registered services in the application,
    including their instantiation status, module location, and associated tags. Services are
    grouped by their module namespace for better organization.
    
    Attributes:
        container: The application's service container instance managing all services.
    """

    def __init__(self):
        super().__init__("service")
        self.container = Application().container

    def execute(self):
        """
        Displays a formatted list of all registered services grouped by their modules.
        Shows service status, instance IDs, and associated tags.
        """
        console = Console()
        print("")

        grouped_services = {}

        for service_class, instance in self.container._instances.items():
            if service_class not in self.container._definitions:
                continue

            definition = self.container._definitions[service_class]

            if service_class.__module__ in [
                "Built-in",
                "builtins",
                "framefox.core.di.service_container",
            ]:
                continue

            tags = definition.tags or []

            group = (
                service_class.__module__.split(".")[1]
                if len(service_class.__module__.split(".")) > 1
                else "other"
            )

            if group not in grouped_services:
                grouped_services[group] = []

            tags_str = ", ".join(sorted(tags)) if tags else "No tags"
            grouped_services[group].append((tags_str, service_class, instance))

        for service_class, definition in self.container._definitions.items():
            if service_class in self.container._instances:
                continue

            if service_class.__module__ in [
                "Built-in",
                "builtins",
                "framefox.core.di.service_container",
            ]:
                continue

            tags = definition.tags or []

            group = (
                service_class.__module__.split(".")[1]
                if len(service_class.__module__.split(".")) > 1
                else "other"
            )

            if group not in grouped_services:
                grouped_services[group] = []

            tags_str = ", ".join(sorted(tags)) if tags else "No tags"
            grouped_services[group].append((tags_str, service_class, None))

        total_services = sum(len(services) for services in grouped_services.values())

        self.printer.print_msg(
            f"Total registered services: {total_services}",
            theme="success",
            linebefore=True,
        )
        print("")

        for group, services in sorted(grouped_services.items()):
            console.print(
                f"Services in group: [bold cyan]{group}[/bold cyan]"
            )

            table = Table(show_header=True, header_style="bold orange1")
            table.add_column("Service", style="bold orange3")
            table.add_column("Module", style="white")
            table.add_column("Instance ID", style="cyan")
            table.add_column("Status", style="magenta")
            table.add_column("Tags", style="green")

            sorted_services = sorted(services, key=lambda x: x[1].__name__)

            for tags_str, service_class, instance in sorted_services:
                status = "Instantiated" if instance else "Not Instantiated"
                if (
                    service_class in self.container._definitions
                    and self.container._definitions[service_class].abstract
                ):
                    status = "Abstract"

                instance_id = str(id(instance)) if instance else "N/A"

                table.add_row(
                    service_class.__name__,
                    service_class.__module__,
                    instance_id,
                    status,
                    tags_str,
                )

            console.print(table)
            print("")
