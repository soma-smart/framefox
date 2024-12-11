# main.py
from flask import Flask
from src.core.router import Router

app = Flask(__name__)

# Initialisation et chargement dynamique des contrôleurs
router = Router(app)
router.register_controllers()

if __name__ == "__main__":
    app.run(debug=True)
