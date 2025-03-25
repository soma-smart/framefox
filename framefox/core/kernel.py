from pathlib import Path
from typing import ClassVar, Optional

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from framefox.core.config.settings import Settings
from framefox.core.debug.exception.debug_exception import DebugException
from framefox.core.debug.handler.debug_handler import DebugHandler
from framefox.core.di.service_container import ServiceContainer
from framefox.core.events.event_dispatcher import dispatcher
from framefox.core.logging.logger import Logger
from framefox.core.middleware.middleware_manager import MiddlewareManager
from framefox.core.routing.router import Router
from framefox.core.security.token_storage import TokenStorage
from framefox.core.security.user.entity_user_provider import EntityUserProvider
from framefox.core.security.user.user_provider import UserProvider
from framefox.core.orm.entity_manager_interface import EntityManagerInterface

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox 
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class Kernel:
    """
    Core kernel of the Framefox framework.
    Implements the Singleton pattern and manages the application lifecycle.
    """

    _instance: ClassVar[Optional["Kernel"]] = None

    def __new__(cls) -> "Kernel":
        """Ensures that only one instance of the Kernel exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initializes the main components of the framework if not already done."""
        if hasattr(self, "_initialized") and self._initialized:
            return

        self._container = ServiceContainer()
        self._settings = self._container.get(Settings)
        self._logger = self._container.get(Logger).get_logger()
        self._init_security_services()
        self._app = self._create_fastapi_app()
        self._configure_app()
        # if self._settings.debug_mode:
        #     self._container.print_container_stats()

        self._initialized = True

    def _init_security_services(self) -> None:
        """Initialise les services liés à la sécurité et l'authentification."""

        session = self._container.get_by_name("Session")
        token_storage = TokenStorage(session)
        self._container.set_instance(TokenStorage, token_storage)
        entity_user_provider = self._container.get(EntityUserProvider)
        user_provider = UserProvider(
            token_storage, session, entity_user_provider)
        self._container.set_instance(UserProvider, user_provider)
        self._container.set_instance(
            EntityManagerInterface, EntityManagerInterface())
        self._logger.debug("Security services initialized")

    def _create_fastapi_app(self) -> FastAPI:
        """Creates and configures the FastAPI instance."""
        return FastAPI(
            debug=self._settings.debug_mode,
            openapi_url=self._settings.openapi_url,
            redoc_url=self._settings.redoc_url,
        )

    def _configure_app(self) -> None:
        """Configures all application components."""
        self._app.add_exception_handler(
            DebugException, DebugHandler.debug_exception_handler
        )
        self._setup_middlewares()
        self._setup_routing()
        self._setup_static_files()
        dispatcher.load_listeners()

    def _setup_middlewares(self) -> None:
        """Configures the application middlewares."""
        middleware_manager = MiddlewareManager(self._app, self._settings)
        middleware_manager.setup_middlewares()

    def _setup_routing(self) -> None:
        """Configures the application routing."""
        router = Router(self._app)
        self._container.set_instance(Router, router)
        router.register_controllers()

    def _setup_static_files(self) -> None:
        """Configures the static files handler."""
        static_path = Path(__file__).parent / "templates" / "static"
        self._app.mount(
            "/static", StaticFiles(directory=static_path), name="static")
        self._app.mount(
            "/", StaticFiles(directory=Path("public")), name="public_assets")

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
