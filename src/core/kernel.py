import os

from fastapi import FastAPI

from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from src.core.routing.router import register_controllers
from src.core.config.settings import Settings
from src.core.middleware.auth_middleware import AuthMiddleware
# from src.core.models import db


class Kernel:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Kernel, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            # Charger les variables d'environnement depuis le fichier .env
            load_dotenv()
            self.app = FastAPI()
            self.setup_app()
            self.initialized = True

    def setup_app(self):
        settings = Settings()

        # Configurer CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Configurer SQLAlchemy
        self.app.state.database_uri = settings.database_uri
        self.app.state.database_echo = settings.database_echo

        # Initialiser SQLAlchemy
        # db.init_app(self.app)


        # Configurer les middlewares
        if settings.is_auth_enabled:
            self.app.add_middleware(
                AuthMiddleware, access_control=settings.access_control)

        # Enregistrer les contrôleurs
        register_controllers(self.app)

        # Configuration de la base de données
        database_url = os.getenv('DATABASE_URL')
        self.app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Initialisation de la base de données
        db.init_app(self.app)

        # Initialiser et enregistrer les contrôleurs
        router = Router(self.app)
        router.register_controllers()

