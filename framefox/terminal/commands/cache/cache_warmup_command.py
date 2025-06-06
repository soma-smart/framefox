import time

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

class CacheWarmupCommand(AbstractCommand):
    """
    Command to warm up ServiceContainer cache for optimal performance.
    
    This command handles pre-loading and caching of all services including
    service discovery, module scanning, service instance pre-loading,
    and cache file generation for faster startup times.
    """

    def __init__(self):
        super().__init__("warmup")

    def execute(self):
        console = Console()
        print("")
        start_time = time.time()

        table = Table(show_header=True, header_style="bold orange1")
        table.add_column("Cache Component", style="bold orange3")
        table.add_column("Status", style="white")
        table.add_column("Details", style="cyan")

        container_start = time.time()
        container = ServiceContainer()
        container_time = time.time() - container_start
        
        discovery_start = time.time()
        discovery_stats = self._force_service_discovery(container)
        discovery_time = time.time() - discovery_start
        table.add_row(
            "Service Discovery",
            "[green]Completed[/green]",
            f"{discovery_stats['total']} services in {discovery_time:.2f}s"
        )

        preload_start = time.time()
        preload_stats = self._preload_essential_services(container)
        preload_time = time.time() - preload_start
        table.add_row(
            "Essential Services",
            "[green]Pre-loaded[/green]",
            f"{preload_stats['loaded']}/{preload_stats['total']} in {preload_time:.2f}s"
        )

        cache_start = time.time()
        cache_stats = self._generate_cache(container)
        cache_time = time.time() - cache_start
        table.add_row(
            "Cache Generation",
            "[green]Saved[/green]",
            f"{cache_stats['services']} services cached in {cache_time:.2f}s"
        )

        validation_start = time.time()
        validation_stats = self._validate_cache(container)
        validation_time = time.time() - validation_start
        table.add_row(
            "Cache Validation",
            "[green]Valid[/green]" if validation_stats['valid'] else "[red]Invalid[/red]",
            f"Validated in {validation_time:.2f}s"
        )

        total_time = time.time() - start_time

        console.print(table)
        print("")
        
        self._display_container_stats(container)
        
        self.printer.print_msg(
            f"✓ ServiceContainer cache warmed up in {total_time:.2f} seconds",
            theme="success",
            linebefore=True,
        )

    def _force_service_discovery(self, container: ServiceContainer) -> dict:
        container._src_scanned = False
        container._src_scan_in_progress = False
        
        container.force_complete_scan()
        
        stats = container.get_stats()
        scan_status = container.get_scan_status()
        
        return {
            'total': stats.get('total_definitions', 0),
            'modules': scan_status.get('scanned_modules_count', 0),
            'src_scanned': scan_status.get('src_scanned', False)
        }

    def _preload_essential_services(self, container: ServiceContainer) -> dict:
        essential_tags = ['essential', 'controller', 'security', 'orm', 'logging']
        loaded_count = 0
        total_count = 0
        
        for tag in essential_tags:
            try:
                services = container.get_all_by_tag(tag)
                total_count += len(services)
                
                for service in services:
                    try:
                        loaded_count += 1
                    except Exception as e:
                        self.printer.print_msg(
                            f"Warning: Could not pre-load service: {e}",
                            theme="warning"
                        )
            except Exception:
                pass
        
        common_services = [
            'Settings', 'Logger', 'Session', 'EntityManagerRegistry',
            'TokenStorage', 'SecurityContextHandler', 'BundleManager'
        ]
        
        for service_name in common_services:
            try:
                service = container.get_by_name(service_name)
                if service:
                    loaded_count += 1
                total_count += 1
            except Exception:
                total_count += 1
        
        return {
            'loaded': loaded_count,
            'total': total_count
        }

    def _generate_cache(self, container: ServiceContainer) -> dict:
        cache_data = container._create_cache_snapshot()
        
        container._save_service_cache(cache_data)
        
        return {
            'services': len(cache_data.get('services', [])),
            'version': cache_data.get('version', 'unknown'),
            'timestamp': cache_data.get('timestamp', 0)
        }

    def _validate_cache(self, container: ServiceContainer) -> dict:
        cache_data = container._cache_manager.load_cache()
        
        if not cache_data:
            return {'valid': False, 'reason': 'Cache file not found or invalid'}
        
        required_keys = ['version', 'timestamp', 'services']
        for key in required_keys:
            if key not in cache_data:
                return {'valid': False, 'reason': f'Missing key: {key}'}
        
        if not container._cache_manager.is_cache_valid(cache_data):
            return {'valid': False, 'reason': 'Cache is not valid or expired'}
        
        return {'valid': True, 'services': len(cache_data.get('services', []))}

    def _display_container_stats(self, container: ServiceContainer):
        stats = container.get_stats()
        
        stats_table = Table(show_header=True, header_style="bold blue")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="white")
        
        stats_table.add_row("Total Definitions", str(stats.get('total_definitions', 0)))
        stats_table.add_row("Instantiated Services", str(stats.get('instantiated_services', 0)))
        stats_table.add_row("Cached Resolutions", str(stats.get('cached_resolutions', 0)))
        stats_table.add_row("Total Aliases", str(stats.get('total_aliases', 0)))
        stats_table.add_row("Total Tags", str(stats.get('total_tags', 0)))
        
        console = Console()
        print("")
        console.print("📊 Container Statistics:", style="bold blue")
        console.print(stats_table)
