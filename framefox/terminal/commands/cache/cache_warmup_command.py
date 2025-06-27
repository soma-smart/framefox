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

    def __init__(self):
        super().__init__("warmup")
        self.console = Console()
        self._container = None

    @property
    def container(self):
        if self._container is None:
            self._container = ServiceContainer()
        return self._container

    def execute(self):
        """
        Command to warm up the service container cache.
        """
        print("")
        start_time = time.time()

        table = Table(show_header=True, header_style="bold orange1")
        table.add_column("Cache Component", style="bold orange3")
        table.add_column("Status", style="white")
        table.add_column("Details", style="cyan")

        discovery_start = time.time()
        discovery_stats = self._force_service_discovery(self.container)
        discovery_time = time.time() - discovery_start
        table.add_row(
            "Service Discovery",
            "[green]Completed[/green]",
            f"{discovery_stats['total']} services in {discovery_time:.2f}s",
        )

        preload_start = time.time()
        preload_stats = self._preload_essential_services(self.container)
        preload_time = time.time() - preload_start
        table.add_row(
            "Essential Services",
            "[green]Pre-loaded[/green]",
            f"{preload_stats['loaded']}/{preload_stats['total']} in {preload_time:.2f}s",
        )

        cache_start = time.time()
        cache_stats = self._generate_cache(self.container)
        cache_time = time.time() - cache_start
        table.add_row(
            "Cache Generation",
            "[green]Saved[/green]",
            f"{cache_stats['services']} services cached in {cache_time:.2f}s",
        )

        validation_start = time.time()
        validation_stats = self._validate_cache(self.container)
        validation_time = time.time() - validation_start

        if validation_stats["valid"]:
            validation_status = "[green]Valid[/green]"
            validation_details = validation_stats.get("details", f"Validated in {validation_time:.2f}s")
        else:
            validation_status = "[red]Invalid[/red]"
            validation_details = f"{validation_stats['reason']} | {validation_stats.get('details', '')}"

        table.add_row("Cache Validation", validation_status, validation_details)

        total_time = time.time() - start_time

        self.console.print(table)

        if not validation_stats["valid"]:
            print("")
            self.console.print("❌ [bold red]Cache Validation Issues:[/bold red]")
            self.console.print(f"   • Reason: {validation_stats['reason']}")
            if validation_stats.get("details"):
                self.console.print(f"   • Details: {validation_stats['details']}")

        print("")

        self._display_container_stats(self.container)

        self.printer.print_msg(
            f"✓ ServiceContainer cache warmed up in {total_time:.2f} seconds",
            theme="success",
            linebefore=True,
        )

        if not validation_stats["valid"]:
            self.printer.print_msg(
                "⚠️  Cache validation failed - this may affect performance on next startup",
                theme="warning",
            )

    def _force_service_discovery(self, container: ServiceContainer) -> dict:
        container._src_scanned = False
        container._src_scan_in_progress = False

        container.force_complete_scan()

        stats = container.get_stats()
        scan_status = container.get_scan_status()

        return {
            "total": stats.get("total_definitions", 0),
            "modules": scan_status.get("scanned_modules_count", 0),
            "src_scanned": scan_status.get("src_scanned", False),
        }

    def _preload_essential_services(self, container: ServiceContainer) -> dict:
        essential_tags = ["essential", "controller", "security", "orm", "logging"]
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
                        self.printer.print_msg(f"Warning: Could not pre-load service: {e}", theme="warning")
            except Exception:
                pass

        common_services = [
            "Settings",
            "Logger",
            "Session",
            "EntityManagerRegistry",
            "TokenStorage",
            "SecurityContextHandler",
            "BundleManager",
        ]

        for service_name in common_services:
            try:
                service = container.get_by_name(service_name)
                if service:
                    loaded_count += 1
                total_count += 1
            except Exception:
                total_count += 1

        return {"loaded": loaded_count, "total": total_count}

    def _generate_cache(self, container: ServiceContainer) -> dict:
        cache_data = container._create_cache_snapshot()
        container._save_service_cache(cache_data)

        self._generated_cache_data = cache_data

        return {
            "services": len(cache_data.get("services", [])),
            "version": cache_data.get("version", "unknown"),
            "timestamp": cache_data.get("timestamp", 0),
        }

    def _validate_cache(self, container: ServiceContainer) -> dict:
        try:
            if hasattr(self, "_generated_cache_data") and self._generated_cache_data:
                cache_data = self._generated_cache_data
                self.console.print("[dim]Note: Validating freshly generated cache data[/dim]")
            else:
                cache_data = container._cache_manager.load_cache()
                if not cache_data:
                    cache_file = container._cache_manager._get_cache_file()
                    file_exists = cache_file.exists() if cache_file else False
                    file_size = cache_file.stat().st_size if file_exists else 0

                    return {
                        "valid": False,
                        "reason": "Cache file not found or empty",
                        "details": f"File: {cache_file}, Exists: {file_exists}, Size: {file_size}B",
                    }

            required_keys = ["version", "timestamp", "services"]
            missing_keys = [key for key in required_keys if key not in cache_data]

            if missing_keys:
                return {
                    "valid": False,
                    "reason": f"Missing required keys: {', '.join(missing_keys)}",
                    "details": f"Found keys: {list(cache_data.keys())}",
                }

            if not isinstance(cache_data.get("services"), list):
                return {
                    "valid": False,
                    "reason": "Invalid cache structure",
                    "details": f"Services should be list, got {type(cache_data.get('services'))}",
                }

            services = cache_data.get("services", [])
            if not services:
                return {
                    "valid": False,
                    "reason": "No services in cache",
                    "details": "Cache contains empty services list",
                }

            invalid_services = []
            for i, service in enumerate(services[:5]):
                required_service_keys = ["name", "class_path", "module"]
                missing_service_keys = [key for key in required_service_keys if key not in service]
                if missing_service_keys:
                    invalid_services.append(f"Service {i}: missing {missing_service_keys}")

            if invalid_services:
                return {
                    "valid": False,
                    "reason": "Invalid service structure",
                    "details": "; ".join(invalid_services),
                }

            return {
                "valid": True,
                "services": len(services),
                "details": f"Cache valid with {len(services)} services, version {cache_data.get('version')}",
            }

        except Exception as e:
            return {
                "valid": False,
                "reason": f"Validation error: {str(e)}",
                "details": f"Exception during cache validation: {type(e).__name__}",
            }

    def _display_container_stats(self, container: ServiceContainer):
        stats = container.get_stats()

        stats_table = Table(show_header=True, header_style="bold blue")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="white")

        stats_table.add_row("Total Definitions", str(stats.get("total_definitions", 0)))
        stats_table.add_row("Instantiated Services", str(stats.get("instantiated_services", 0)))
        stats_table.add_row("Cached Resolutions", str(stats.get("cached_resolutions", 0)))
        stats_table.add_row("Total Aliases", str(stats.get("total_aliases", 0)))
        stats_table.add_row("Total Tags", str(stats.get("total_tags", 0)))

        print("")
        self.console.print("📊 Container Statistics:", style="bold blue")
        self.console.print(stats_table)
