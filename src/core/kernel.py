import os
from flask import Flask
from src.core.orm.config.database import db
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

        # Configuration de la base de données
        database_url = os.getenv('DATABASE_URL')
        self.app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Initialisation de la base de données
        db.init_app(self.app)

        # Initialiser et enregistrer les contrôleurs
        router = Router(self.app)
        router.register_controllers()

    def run(self):
        with self.app.app_context():
            db.create_all()  # Crée la base de données vide
        self.app.run(debug=self.app.config['DEBUG'])
