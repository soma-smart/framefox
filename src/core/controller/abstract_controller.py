from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter


import inspect


class AbstractController:
    """Classe de base pour tous les contrôleurs."""

    def __init__(self):
        self.router = APIRouter()

        self.register_routes()

    def register_routes(self):
        """
        Parcourt toutes les méthodes de la classe et enregistre celles décorées avec @Route.
        """
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(method, 'route_info'):
                route = method.route_info
                self.router.add_api_route(
                    path=route['path'],
                    endpoint=method,
                    name=route['name'],
                    methods=route['methods']
                )

    def redirect(self, location: str, code: int = 302):
        """Redirige vers une URL spécifique."""
        return RedirectResponse(url=location, status_code=code)

    def render(self, request, template_name: str, context_list: list):
        """Rend une vue avec des variables de contexte."""
        templates = Jinja2Templates(directory="templates")
        context = dict(context_list)
        context["request"] = request
        return templates.TemplateResponse(template_name, context)

    def flash(self, message: str, category: str = "message"):
        """Ajoute un message flash à la session."""
        pass  # Implémentation personnalisée nécessaire

    def json(self, data: dict, status: int = 200):
        """Renvoie une réponse JSON."""
        return JSONResponse(content=data, status_code=status)
