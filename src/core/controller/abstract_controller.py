
from flask import redirect, render_template, flash, jsonify, request


class AbstractController:
    """Classe de base pour tous les contrôleurs."""

    def __init__(self):
        self.routes = []

    def add_route(self, path, endpoint, view_func, methods=["GET"]):
        """Ajoute une route à la liste des routes du contrôleur."""
        self.routes.append({
            "path": path,
            "endpoint": endpoint,
            "view_func": view_func,
            "methods": methods,
        })

    def redirect(self, location, code=302):
        """Redirige vers une URL spécifique."""
        return redirect(location, code)

    def render_template(self, template_name, **context):
        """Rend une vue Flask avec des variables de contexte."""
        return render_template(template_name, **context)

    def flash(self, message, category="message"):
        """Ajoute un message flash à la session."""
        flash(message, category)

    def jsonify(self, data, status=200, **kwargs):
        """Renvoie une réponse JSON."""
        return jsonify(data), status

    def request(self):
        """Renvoie l'objet de requête actuel."""
        return request
