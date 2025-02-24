import inspect

from rich.console import Console
from rich.table import Table

from framefox.core.di.service_container import ServiceContainer
from framefox.terminal.commands.abstract_command import AbstractCommand

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class DebugServiceCommand(AbstractCommand):
    def __init__(self):
        super().__init__("service")
        self.container = ServiceContainer()

    def execute(self):
        """
        Display the list of registered services
        """
        console = Console()
        print("")

        grouped_services = {}
        for service_class, instance in self.container.services.items():
            if service_class.__module__ in [
                "Built-in",
                "builtins",
                "framefox.core.di.service_container",
            ]:
                continue

            tags = []
            for tag, services in self.container.tags.items():
                if instance in services:
                    tags.append(tag)
            group = (
                service_class.__module__.split(".")[1]
                if len(service_class.__module__.split(".")) > 1
                else "other"
            )

            if group not in grouped_services:
                grouped_services[group] = []

            tags_str = ", ".join(sorted(tags)) if tags else "No tags"
            grouped_services[group].append((tags_str, service_class, instance))

        total_services = sum(len(services) for services in grouped_services.values())

        self.printer.print_msg(
            f"Total registered services: {total_services}",
            theme="success",
            linebefore=True,
        )
        print("")

        for group, services in sorted(grouped_services.items()):

            console.print(
                f"Services in group: [bold cyan]{
                    group}[/bold cyan]"
            )

            table = Table(show_header=True, header_style="bold orange1")
            table.add_column("Service", style="bold orange3")
            table.add_column("Module", style="white")
            table.add_column("Instance ID", style="cyan")
            table.add_column("Tags", style="green")

            sorted_services = sorted(services, key=lambda x: x[1].__name__)

            for tags_str, service_class, instance in sorted_services:
                table.add_row(
                    service_class.__name__,
                    service_class.__module__,
                    str(id(instance)),
                    tags_str,
                )

            console.print(table)
            print("")
