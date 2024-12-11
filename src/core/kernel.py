import os
from flask import Flask
from dotenv import load_dotenv
from src.core.routing.router import Router


class Kernel:
    def __init__(self):
        # Charger les variables d'environnement depuis le fichier .env
        load_dotenv()
        self.app = Flask(__name__)
        self.setup_app()

    def setup_app(self):
        # Récupérer la variable d'environnement APP_ENV
        app_env = os.getenv('APP_ENV', 'prod')
        debug_mode = True if app_env == 'dev' else False

        # Configurer l'application Flask
        self.app.config['DEBUG'] = debug_mode

        # Initialiser et enregistrer les contrôleurs
        router = Router(self.app)
        router.register_controllers()

    def run(self):
        self.app.run(debug=self.app.config['DEBUG'])
