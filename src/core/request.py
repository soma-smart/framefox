# src/core/request.py
from flask import request


class Request:
    """Classe qui encapsule les informations d'une requête HTTP."""

    def __init__(self, flask_request):
        self._request = flask_request

    @property
    def method(self):
        """Retourne la méthode HTTP de la requête (GET, POST, etc.)."""
        return self._request.method

    @property
    def path(self):
        """Retourne le chemin de la requête."""
        return self._request.path

    @property
    def data(self):
        """Retourne le corps de la requête (pour les POST, PUT, etc.)."""
        return self._request.data

    @property
    def json(self):
        """Retourne les données JSON de la requête."""
        return self._request.get_json()

    @property
    def form(self):
        """Retourne les données de formulaire de la requête."""
        return self._request.form

    @property
    def args(self):
        """Retourne les arguments de la requête (query parameters)."""
        return self._request.args

    @property
    def headers(self):
        """Retourne les en-têtes de la requête."""
        return self._request.headers

    @property
    def cookies(self):
        """Retourne les cookies de la requête."""
        return self._request.cookies

    def get_json(self, force=False, silent=False, cache=False):
        """Retourne le JSON de la requête de manière propre."""
        return self._request.get_json(force=force, silent=silent, cache=cache)

    def is_json(self):
        """Vérifie si le type de contenu est JSON."""
        return self._request.is_json
