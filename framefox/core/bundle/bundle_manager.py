import logging
from typing import Dict

import pkg_resources

from framefox.core.bundle.abstract_bundle import AbstractBundle
from framefox.core.di.service_container import ServiceContainer
from framefox.terminal.command_registry import CommandRegistry

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class BundleManager:
    """
    Manages the discovery, initialization, and loading of bundles.
    """

    def __init__(self):
        self.bundles: Dict[str, AbstractBundle] = {}
        self.logger = logging.getLogger("BUNDLE_MANAGER")

    def discover_bundles(self) -> None:
        """Discovers all bundles installed via entry points"""
        for entry_point in pkg_resources.iter_entry_points("framefox.bundles"):
            try:
                bundle_class = entry_point.load()
                bundle = bundle_class()
                self.bundles[bundle.name] = bundle
            except Exception as e:
                self.logger.error(f"Error loading bundle {entry_point.name}: {str(e)}")

    def register_bundle_services(self, container: ServiceContainer) -> None:
        """Registers services for all bundles"""
        for name, bundle in self.bundles.items():
            try:
                bundle.register_services(container)
            except Exception as e:
                self.logger.error(f"Error registering services for bundle {name}: {str(e)}")

    def register_bundle_commands(self, registry: CommandRegistry) -> None:
        """Registers commands for all bundles"""
        for name, bundle in self.bundles.items():
            try:
                bundle.register_commands(registry)
            except Exception as e:
                self.logger.error(f"Error registering commands for bundle {name}: {str(e)}")

    def boot_bundles(self, container: ServiceContainer) -> None:
        """Boots all bundles after complete initialization"""
        for name, bundle in self.bundles.items():
            try:
                bundle.boot(container)
            except Exception as e:
                self.logger.error(f"Error booting bundle {name}: {str(e)}")

    def get_bundle(self, name: str) -> AbstractBundle:
        """Retrieves a bundle by its name"""
        if name not in self.bundles:
            raise ValueError(f"Bundle '{name}' not found")
        return self.bundles[name]

    def has_bundle(self, name: str) -> bool:
        """Checks if a bundle is loaded"""
        return name in self.bundles
