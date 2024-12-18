from typing import Annotated
from fastapi import FastAPI
from injectable import autowired, Autowired, load_injection_container
from src.core.routing.router import Router
from src.core.middleware.middleware_manager import MiddlewareManager
from src.core.logging.logger import Logger
from src.core.config.settings import Settings

# Importer l'instance globale
from src.core.events.event_dispatcher import dispatcher


class Kernel:
    load_injection_container()
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Kernel, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @autowired
    def __init__(self, settings: Annotated[Settings, Autowired]):
        self.settings = settings
        if not hasattr(self, "initialized"):
            self.app = FastAPI(debug=self.settings.debug_mode)
            self.logger = Logger().get_logger()

            dispatcher.load_listeners()

            # Configurer les middlewares
            self.setup_app()
            self.initialized = True

    def setup_app(self):
        middleware_manager = MiddlewareManager(self.app, self.settings)
        middleware_manager.setup_middlewares()
        router = Router(self.app)
        router.register_controllers()
