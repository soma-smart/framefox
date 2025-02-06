from fastapi import FastAPI


from framefox.core.config.setup_pp_debug import setup_pp_debug
from framefox.core.routing.router import Router
from framefox.core.logging.logger import Logger
from framefox.core.config.settings import Settings
from framefox.core.events.event_dispatcher import dispatcher
from framefox.core.middleware.middleware_manager import MiddlewareManager
from framefox.core.debug.handler.debug_handler import DebugHandler
from framefox.core.debug.exception.debug_exception import DebugException
from framefox.core.di.service_container import ServiceContainer
from fastapi.staticfiles import StaticFiles
from pathlib import Path

INITIALIZED = False


class Kernel:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Kernel, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        container = ServiceContainer()
        self.settings = container.get(Settings)
        global INITIALIZED
        if not INITIALIZED:
            self.app = FastAPI(
                debug=self.settings.debug_mode,
                openapi_url=self.settings.openapi_url,
                redoc_url=self.settings.redoc_url,
            )
            self.app.add_exception_handler(
                DebugException, DebugHandler.debug_exception_handler
            )
            self.logger = Logger().get_logger()
            dispatcher.load_listeners()
            self.setup_app()
            INITIALIZED = True

    def setup_app(self):
        setup_pp_debug()

        middleware_manager = MiddlewareManager(self.app, self.settings)
        middleware_manager.setup_middlewares()
        router = Router(self.app)
        router.register_controllers()
        self.app.mount(
            "/static",
            StaticFiles(directory=Path(__file__).parent / "templates" / "static"),
            name="static",
        )
