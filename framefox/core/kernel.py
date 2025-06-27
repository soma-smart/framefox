import logging
from pathlib import Path
from typing import ClassVar, Optional

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from framefox.core.config.settings import Settings
from framefox.core.events.event_dispatcher import dispatcher
from framefox.core.logging.logger import Logger
from framefox.core.middleware.middleware_manager import MiddlewareManager
from framefox.core.routing.router import Router

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class Kernel:
    """
    The Kernel class is the core of the Framefox framework. It initializes and configures
    the FastAPI application, manages dependency injection, bundles, security services,
    middleware, routing, and static files. It provides access to the main FastAPI app,
    configuration settings, and logger.
    """

    _instance: ClassVar[Optional["Kernel"]] = None

    def __init__(self, container=None, bundle_manager=None) -> None:
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._container = container
        self._bundle_manager = bundle_manager

        try:
            self._settings = Settings()
            self._logger = logging.getLogger("KERNEL")
            self._app = self._create_fastapi_app()
            self._configure_app()
            self._initialized = True

        except Exception as e:
            self._logger.error(f"Failed to initialize Kernel: {e}")
            raise RuntimeError(f"Kernel initialization failed: {e}") from e

    def _create_fastapi_app(self) -> FastAPI:
        """Create FastAPI application with proper configuration"""
        return FastAPI(
            debug=self._settings.is_debug,
            openapi_url=self._settings.openapi_url if self._settings.is_debug else None,
            redoc_url=self._settings.redoc_url if self._settings.is_debug else None,
            docs_url="/docs" if self._settings.is_debug else None,
            title="Framefox Application",
            version="1.0.0",
        )

    def _configure_app(self) -> None:
        """Configure the FastAPI application"""
        MiddlewareManager(self._app).setup_middlewares()
        self._setup_routing()
        self._setup_static_files()
        self._bundle_manager.boot_bundles(self._container)
        dispatcher.load_listeners()
        self._container.freeze_registry()

        self._logger.debug("Framefox application initialized successfully")
        self._logger.debug("Application configuration complete - registry frozen")

    def _setup_routing(self) -> None:
        """Setup routing system and register controllers"""
        router = Router(self._app)
        self._container.set_instance(Router, router)
        router.register_controllers()

        self._logger.debug("Routing system configured")

    def _setup_static_files(self) -> None:
        """Setup static file serving"""
        try:
            static_path = Path(__file__).parent / "templates" / "static"
            if static_path.exists():
                self._app.mount("/static", StaticFiles(directory=static_path), name="static")
                self._logger.debug(f"Framework static files mounted: {static_path}")

            profiler_path = static_path / "profiler"
            profiler_path.mkdir(parents=True, exist_ok=True)

            public_path = Path("public")
            if public_path.exists():
                self._app.mount("/", StaticFiles(directory=public_path), name="public_assets")
                self._logger.debug(f"Public assets mounted: {public_path}")

        except Exception as e:
            self._logger.warning(f"Failed to setup some static files: {e}")

    @property
    def app(self) -> FastAPI:
        """Returns the configured FastAPI instance."""
        return self._app

    @property
    def settings(self) -> Settings:
        """Returns the configuration settings."""
        return self._settings

    @property
    def logger(self) -> Logger:
        """Returns the configured logger."""
        return self._logger
