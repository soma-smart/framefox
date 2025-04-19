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
    def __init__(self):
        super().__init__()
        self.container = Application().container


    def execute(self):
        """
        Display the list of registered services
        """
        console = Console()
        print("")

        grouped_services = {}

        # Itérer sur les instances disponibles plutôt que sur 'services'
        for service_class, instance in self.container._instances.items():
            # Vérifier si on a une définition pour cette classe
            if service_class not in self.container._definitions:
                continue

            # Récupérer la définition (pour les tags, etc.)
            definition = self.container._definitions[service_class]

            if service_class.__module__ in [
                "Built-in",
                "builtins",
                "framefox.core.di.service_container",
            ]:
                continue

            # Les tags sont maintenant stockés dans la définition du service
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

        # Afficher aussi les services définis mais non instanciés
        for service_class, definition in self.container._definitions.items():
            if service_class in self.container._instances:
                continue  # Déjà traité

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
            # L'instance est None car le service n'est pas encore instancié
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
                f"Services in group: [bold cyan]{
                    group}[/bold cyan]"
            )

            table = Table(show_header=True, header_style="bold orange1")
            table.add_column("Service", style="bold orange3")
            table.add_column("Module", style="white")
            table.add_column("Instance ID", style="cyan")
            table.add_column("Status", style="magenta")
            table.add_column("Tags", style="green")

            sorted_services = sorted(services, key=lambda x: x[1].__name__)

            for tags_str, service_class, instance in sorted_services:
                # Déterminer le statut du service
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
