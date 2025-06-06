import time
from pathlib import Path
from rich.console import Console
from rich.table import Table

from framefox.core.di.service_container import ServiceContainer
from framefox.terminal.commands.abstract_command import AbstractCommand

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""
class CacheClearCommand(AbstractCommand):
    """
    Command to clear ServiceContainer cache files and force cache rebuild.
    
    Handles clearing all service-related cache files including service definition cache files,
    module scan cache, service resolution cache, and development/production cache files.
    Also clears memory caches and resets service instances to force re-instantiation.
    """

    def __init__(self):
        super().__init__("clear")
        self.cache_dir = Path("var/cache")

    def execute(self):
        console = Console()
        print("")
        start_time = time.time()

        table = Table(show_header=True, header_style="bold orange1")
        table.add_column("Cache Component", style="bold orange3")
        table.add_column("Status", style="white")
        table.add_column("Details", style="cyan")

        cache_files_cleared = self._clear_cache_files()
        table.add_row(
            "Service Cache Files",
            "[green]Cleared[/green]" if cache_files_cleared > 0 else "[yellow]Empty[/yellow]",
            f"{cache_files_cleared} files removed"
        )

        container = ServiceContainer()
        memory_stats = self._clear_memory_caches(container)
        table.add_row(
            "Memory Caches",
            "[green]Cleared[/green]",
            f"Resolution: {memory_stats['resolution']}, Modules: {memory_stats['modules']}"
        )

        instances_cleared = self._clear_service_instances(container)
        table.add_row(
            "Service Instances",
            "[green]Cleared[/green]" if instances_cleared > 0 else "[yellow]Empty[/yellow]",
            f"{instances_cleared} instances removed"
        )

        scan_status = self._reset_scan_status(container)
        table.add_row(
            "Scan Status",
            "[green]Reset[/green]",
            f"Modules: {scan_status['modules']}, Sources: {scan_status['sources']}"
        )

        total_time = time.time() - start_time

        console.print(table)
        print("")
        
        self.printer.print_msg(
            f"✓ ServiceContainer cache cleared in {total_time:.2f} seconds",
            theme="success",
            linebefore=True,
        )
        
        self.printer.print_msg(
            "Next server start will rebuild the service cache automatically",
            theme="info",
        )

    def _clear_cache_files(self) -> int:
        cleared_count = 0
        
        cache_files = [
            self.cache_dir / "dev_services.json",
            self.cache_dir / "services.json",
            self.cache_dir / "service_definitions.json",
        ]
        
        for cache_file in cache_files:
            if cache_file.exists():
                try:
                    cache_file.unlink()
                    cleared_count += 1
                except Exception as e:
                    self.printer.print_msg(
                        f"Warning: Could not remove {cache_file.name}: {e}",
                        theme="warning"
                    )
        
        return cleared_count

    def _clear_memory_caches(self, container: ServiceContainer) -> dict:
        resolution_count = len(container._resolution_cache)
        modules_count = len(container._module_scan_cache)
        
        container.cleanup_memory()
        
        return {
            'resolution': resolution_count,
            'modules': modules_count
        }

    def _clear_service_instances(self, container: ServiceContainer) -> int:
        instances_count = len(container._instances)
        
        essential_services = []
        for service_class, instance in container._instances.items():
            if hasattr(instance, '__module__'):
                module_name = instance.__module__
                if any(essential in module_name for essential in ['settings', 'logger', 'config']):
                    essential_services.append((service_class, instance))
        
        container._instances.clear()
        
        for service_class, instance in essential_services:
            container._instances[service_class] = instance
        
        return instances_count - len(essential_services)

    def _reset_scan_status(self, container: ServiceContainer) -> dict:
        modules_count = len(container._scanned_modules)
        sources_scanned = container._src_scanned
        
        container._scanned_modules.clear()
        container._src_scanned = False
        container._src_scan_in_progress = False
        
        return {
            'modules': modules_count,
            'sources': 'Yes' if sources_scanned else 'No'
        }
