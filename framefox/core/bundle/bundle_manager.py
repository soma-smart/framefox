import logging
from importlib.metadata import entry_points
from typing import Dict

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
    BundleManager is responsible for discovering, initializing, and managing bundles
    within the Framefox framework. It loads bundles via entry points, registers their
    services and commands, and handles their bootstrapping process.
    """

    def __init__(self):
        self.bundles: Dict[str, AbstractBundle] = {}
        self.logger = logging.getLogger("BUNDLE_MANAGER")

    def discover_bundles(self) -> None:
        try:
            eps = entry_points()
            if hasattr(eps, "select"):
                bundle_entries = eps.select(group="framefox.bundles")
            else:
                bundle_entries = eps.get("framefox.bundles", [])
            for entry_point in bundle_entries:
                try:
                    bundle_class = entry_point.load()
                    bundle = bundle_class()
                    self.bundles[bundle.name] = bundle
                    self.logger.debug(f"Loaded bundle: {bundle.name}")
                except Exception as e:
                    self.logger.error(f"Error loading bundle {entry_point.name}: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error discovering bundles: {str(e)}")

    def register_bundle_services(self, container: ServiceContainer) -> None:
        for name, bundle in self.bundles.items():
            try:
                bundle.register_services(container)
                self.logger.debug(f"Registered services for bundle: {name}")
            except Exception as e:
                self.logger.error(f"Error registering services for bundle {name}: {str(e)}")

    def register_bundle_commands(self, registry: CommandRegistry) -> None:
        for name, bundle in self.bundles.items():
            try:
                bundle.register_commands(registry)
                self.logger.debug(f"Registered commands for bundle: {name}")
            except Exception as e:
                self.logger.error(f"Error registering commands for bundle {name}: {str(e)}")

    def boot_bundles(self, container: ServiceContainer) -> None:
        for name, bundle in self.bundles.items():
            try:
                bundle.boot(container)
                self.logger.debug(f"Booted bundle: {name}")
            except Exception as e:
                self.logger.error(f"Error booting bundle {name}: {str(e)}")

    def get_bundle(self, name: str) -> AbstractBundle:
        if name not in self.bundles:
            raise ValueError(f"Bundle '{name}' not found")
        return self.bundles[name]

    def has_bundle(self, name: str) -> bool:
        return name in self.bundles

    def list_bundles(self) -> Dict[str, str]:
        return {name: getattr(bundle, "description", "No description available") for name, bundle in self.bundles.items()}
