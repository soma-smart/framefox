from framefox.core.bundle.bundle_manager import BundleManager
from framefox.core.di.service_container import ServiceContainer

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""

class Application:
    """
    Central entry point for all interactions with the application,
    whether via web or CLI.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self._container = ServiceContainer()
        self._bundle_manager = BundleManager()
        self._bundle_manager.discover_bundles()
        self._container.set_instance(BundleManager, self._bundle_manager)
        self._bundle_manager.register_bundle_services(self._container)
        self._initialized = True

    def boot_web(self):
        from framefox.core.kernel import Kernel
        kernel = Kernel(self._container, self._bundle_manager)
        return kernel

    @property
    def container(self):
        return self._container

    @property
    def bundle_manager(self):
        return self._bundle_manager
