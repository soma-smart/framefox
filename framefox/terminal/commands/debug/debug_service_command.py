from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from framefox.application import Application
from framefox.terminal.commands.abstract_command import AbstractCommand

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
        super().__init__()
        self.container = Application().container

    def execute(self):
        """
        Displays a formatted list of all registered services grouped by their modules.\n
        Shows service status, instance IDs, and associated tags.\n
        """
        console = Console()
        print("")

        scan_status = self.container.get_scan_status()
        if not scan_status["src_scanned"]:
            console.print("🔄 [yellow]Src services not yet scanned. Forcing complete scan...[/yellow]")
            self.container.force_complete_scan()
            console.print("✅ [green]Complete scan finished[/green]")
            print("")

        self._display_container_stats(console)

        grouped_services = self._group_services()

        total_services = sum(len(services) for services in grouped_services.values())

        self.printer.print_msg(
            f"Total registered services: {total_services}",
            theme="success",
            linebefore=True,
        )
        print("")

        for group, services in sorted(grouped_services.items()):
            self._display_service_group(console, group, services)

    def _display_container_stats(self, console: Console) -> None:
        stats = self.container.get_stats()

        stats_text = Text()
        stats_text.append("Service Container Statistics\n", style="bold cyan")
        stats_text.append(f"• Total definitions: {stats['total_definitions']}\n", style="white")
        stats_text.append(
            f"• Instantiated services: {stats['instantiated_services']}\n",
            style="green",
        )
        stats_text.append(f"• Cached resolutions: {stats['cached_resolutions']}\n", style="yellow")
        stats_text.append(f"• Total aliases: {stats['total_aliases']}\n", style="blue")
        stats_text.append(f"• Total tags: {stats['total_tags']}\n", style="magenta")
        stats_text.append(
            f"• Registered factories: {stats['registered_factories']}\n",
            style="orange1",
        )
        stats_text.append(
            f"• Registry frozen: {stats['frozen']}\n",
            style="red" if stats["frozen"] else "green",
        )

        scan_status = self.container.get_scan_status()
        stats_text.append("\nLazy Scan Status:\n", style="bold yellow")
        stats_text.append(
            f"• Src scanned: {scan_status['src_scanned']}\n",
            style="green" if scan_status["src_scanned"] else "red",
        )
        stats_text.append(
            f"• Src scan in progress: {scan_status['src_scan_in_progress']}\n",
            style="yellow" if scan_status["src_scan_in_progress"] else "white",
        )
        stats_text.append(f"• Scanned modules: {scan_status['scanned_modules_count']}\n", style="cyan")
        stats_text.append(f"• Cached modules: {scan_status['cached_modules_count']}\n", style="cyan")
        stats_text.append(f"• Src paths found: {scan_status['src_paths_count']}\n", style="cyan")
        stats_text.append(
            f"• Background scan enabled: {scan_status['background_scan_enabled']}\n",
            style="cyan",
        )

        stats_text.append("\nFiltering Info:\n", style="bold yellow")
        stats_text.append("• Framework services only\n", style="cyan")
        stats_text.append("• External libraries excluded\n", style="cyan")
        stats_text.append("• Built-in modules excluded", style="cyan")

        panel = Panel(stats_text, title="Container Overview", border_style="cyan")
        console.print(panel)
        print("")

    def _group_services(self) -> dict:
        grouped_services = {}

        all_definitions = self.container._registry.get_all_definitions()

        for service_class, definition in all_definitions.items():
            if self._should_exclude_service(service_class):
                continue

            group = self._get_service_group(service_class)

            if group not in grouped_services:
                grouped_services[group] = []

            instance = self.container._instances.get(service_class)

            tags_str = ", ".join(sorted(definition.tags)) if definition.tags else "No tags"

            grouped_services[group].append(
                {
                    "service_class": service_class,
                    "definition": definition,
                    "instance": instance,
                    "tags_str": tags_str,
                }
            )

        return grouped_services

    def _should_exclude_service(self, service_class) -> bool:
        excluded_modules = [
            "Built-in",
            "builtins",
            "framefox.core.di.service_container",
            "framefox.core.di.service_registry",
            "framefox.core.di.service_factory_manager",
            "framefox.core.di.service_definition",
        ]

        return service_class.__module__ in excluded_modules

    def _get_service_group(self, service_class) -> str:
        module_parts = service_class.__module__.split(".")

        if len(module_parts) > 1:
            if module_parts[0] in ["framefox", "src"]:
                if len(module_parts) > 2:
                    return module_parts[1]
                else:
                    return module_parts[1]
            else:
                return module_parts[0]

        return "other"

    def _display_service_group(self, console: Console, group: str, services: list) -> None:
        console.print(f"Services in group: [bold cyan]{group}[/bold cyan] ({len(services)} services)")

        table = Table(show_header=True, header_style="bold orange1")
        table.add_column("Service", style="bold orange3", no_wrap=True)
        table.add_column("Module", style="white")
        table.add_column("Instance ID", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Visibility", style="blue")
        table.add_column("Tags", style="green")

        sorted_services = sorted(services, key=lambda x: x["service_class"].__name__)

        for service_info in sorted_services:
            service_class = service_info["service_class"]
            definition = service_info["definition"]
            instance = service_info["instance"]
            tags_str = service_info["tags_str"]

            status = self._get_service_status(service_class, definition, instance)

            visibility = "Public" if definition.public else "Private"

            instance_id = str(id(instance)) if instance else "N/A"

            status_style = self._get_status_style(status)

            table.add_row(
                service_class.__name__,
                service_class.__module__,
                instance_id,
                f"[{status_style}]{status}[/{status_style}]",
                visibility,
                tags_str,
            )

        console.print(table)
        print("")

    def _get_service_status(self, service_class, definition, instance) -> str:
        if definition.abstract:
            return "Abstract"
        elif instance is not None:
            return "Instantiated"
        elif definition.synthetic:
            return "Synthetic"
        elif definition.lazy:
            return "Lazy"
        else:
            return "Not Instantiated"

    def _get_status_style(self, status: str) -> str:
        status_styles = {
            "Instantiated": "green",
            "Not Instantiated": "yellow",
            "Abstract": "red",
            "Synthetic": "blue",
            "Lazy": "cyan",
        }
        return status_styles.get(status, "white")

    def _display_detailed_service_info(self, console: Console, service_class, definition, instance) -> None:
        details = Text()
        details.append(f"Service: {service_class.__name__}\n", style="bold cyan")
        details.append(f"Module: {service_class.__module__}\n", style="white")
        details.append(f"Public: {definition.public}\n", style="blue")
        details.append(f"Autowire: {definition.autowire}\n", style="green")
        details.append(f"Abstract: {definition.abstract}\n", style="red")
        details.append(f"Synthetic: {definition.synthetic}\n", style="magenta")
        details.append(f"Lazy: {definition.lazy}\n", style="yellow")

        if definition.factory:
            details.append(f"Factory: {definition.factory}\n", style="orange1")

        if definition.arguments:
            details.append(f"Arguments: {definition.arguments}\n", style="purple")

        if definition.method_calls:
            details.append(f"Method calls: {definition.method_calls}\n", style="dark_orange")

        if instance:
            details.append(f"Instance ID: {id(instance)}\n", style="cyan")
            details.append(f"Instance type: {type(instance)}\n", style="bright_cyan")

        panel = Panel(
            details,
            title=f"Service Details: {service_class.__name__}",
            border_style="green",
        )
        console.print(panel)
