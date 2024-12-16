
from fastapi import FastAPI
from injectable import autowired, Autowired, load_injection_container
from src.core.routing.router import Router
from src.core.middleware.middleware_manager import MiddlewareManager
from src.core.logging.logger import Logger
from src.core.config.settings import Settings


load_injection_container()


class Kernel:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Kernel, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @autowired
    def __init__(self, settings: Autowired(Settings)):
        self.settings = settings
        if not hasattr(self, 'initialized'):
            # Utiliser les paramètres pour configurer l'application FastAPI
            self.app = FastAPI(debug=self.settings.debug_mode)
            # Configurer le logger
            self.logger = Logger().get_logger()
            # Configurer l'application
            self.setup_app()
            self.initialized = True

    def setup_app(self):
        # Configurer les middlewares
        middleware_manager = MiddlewareManager(self.app, self.settings)
        middleware_manager.setup_middlewares()
        # Enregistrer les contrôleurs
        Router.register_controllers(self.app)
