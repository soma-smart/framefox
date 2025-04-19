import os
import time

from rich.console import Console
from rich.table import Table

from framefox.core.config.settings import Settings
from framefox.core.di.service_container import ServiceContainer
from framefox.core.kernel import Kernel
from framefox.core.templates.template_renderer import TemplateRenderer
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
        super().__init__()
        self.kernel = Kernel()
        self.container = ServiceContainer()
        self.settings = self.container.get(Settings)
        self.template_renderer = self.container.get(TemplateRenderer)

    def execute(self):
        """
        Warm up the application cache
        """
        console = Console()
        print("")
        start_time = time.time()

        table = Table(show_header=True, header_style="bold orange1")
        table.add_column("Component", style="bold orange3")
        table.add_column("Status", style="white")
        table.add_column("Time", style="white")

        template_start = time.time()
        template_count = self._warmup_templates()
        template_time = time.time() - template_start
        table.add_row(
            "Templates",
            f"[green]{template_count} loaded[/green]",
            f"{template_time:.2f}s",
        )

        route_start = time.time()
        route_count = self._warmup_routes()
        route_time = time.time() - route_start
        table.add_row(
            "Routes", f"[green]{route_count} loaded[/green]", f"{route_time:.2f}s"
        )

        service_start = time.time()
        service_count = self._warmup_services()
        service_time = time.time() - service_start
        table.add_row(
            "Services", f"[green]{service_count} loaded[/green]", f"{service_time:.2f}s"
        )

        total_time = time.time() - start_time

        console.print(table)
        print("")
        self.printer.print_msg(
            f"✓ Cache warmed up in {total_time:.2f} seconds",
            theme="success",
            linebefore=True,
        )

    def _warmup_templates(self) -> int:
        count = 0
        template_dir = "templates"
        for root, _, files in os.walk(template_dir):
            for file in files:
                if file.endswith(".html"):
                    template_path = os.path.join(root, file)
                    relative_path = os.path.relpath(template_path, template_dir)
                    try:
                        self.template_renderer.env.get_template(relative_path)
                        count += 1
                    except:
                        pass
        return count

    def _warmup_routes(self) -> int:
        return len(self.kernel.app.routes)

    def _warmup_services(self) -> int:
        return len(self.container.services)
