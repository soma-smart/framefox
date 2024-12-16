import os
from fastapi import FastAPI
from src.core.routing.router import register_controllers
from src.core.config.settings import Settings
from src.core.middleware.middleware_manager import MiddlewareManager
from src.core.orm.database import Database
from src.core.logging.logger import Logger


class Kernel:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Kernel, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            # Instancier les paramètres de configuration
            self.settings = Settings()

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

        # Initialiser la base de données
        self.database = Database(self.settings)

        # Enregistrer les contrôleurs
        register_controllers(self.app)
