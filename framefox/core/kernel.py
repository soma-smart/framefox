import logging
from pathlib import Path
from typing import ClassVar, Optional

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from framefox.core.config.settings import Settings
from framefox.core.debug.exception.debug_exception import DebugException
from framefox.core.debug.handler.debug_handler import DebugHandler
from framefox.core.events.event_dispatcher import dispatcher
from framefox.core.logging.logger import Logger
from framefox.core.middleware.middleware_manager import MiddlewareManager
from framefox.core.orm.entity_manager_interface import EntityManagerInterface
from framefox.core.routing.router import Router
from framefox.core.security.handlers.security_context_handler import (
    SecurityContextHandler,
)
from framefox.core.security.token_storage import TokenStorage
from framefox.core.security.user.entity_user_provider import EntityUserProvider
from framefox.core.security.user.user_provider import UserProvider

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
        return FastAPI(
            debug=self._settings.is_debug,
            openapi_url=self._settings.openapi_url,
            redoc_url=self._settings.redoc_url,
        )

    def _configure_app(self) -> None:
        self._app.add_exception_handler(
            DebugException, DebugHandler.debug_exception_handler
        )
        self._setup_middlewares()
        self._setup_routing()
        self._setup_static_files()
        self._bundle_manager.boot_bundles(self._container)
        dispatcher.load_listeners()
        self._container.freeze_registry()
        self._logger.debug("Application configuration complete - registry frozen")

    def _setup_middlewares(self) -> None:
        middleware_manager = MiddlewareManager(self._app, self._settings)
        middleware_manager.setup_middlewares()

    def _setup_routing(self) -> None:
        router = Router(self._app)
        self._container.set_instance(Router, router)

        if self._settings.app_env == "dev":
            router._register_profiler_routes()
        router.register_controllers()

    def _setup_static_files(self) -> None:
        static_path = Path(__file__).parent / "templates" / "static"
        self._app.mount("/static", StaticFiles(directory=static_path), name="static")

        profiler_path = static_path / "profiler"
        profiler_path.mkdir(parents=True, exist_ok=True)

        self._app.mount(
            "/", StaticFiles(directory=Path("public")), name="public_assets"
        )

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
