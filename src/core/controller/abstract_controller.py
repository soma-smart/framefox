from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates


class AbstractController:
    """Classe de base pour tous les contrôleurs."""

    def __init__(self):
        self.router = APIRouter()

    def add_route(self, path: str, endpoint: str, view_func, methods=["GET"]):
        """Ajoute une route à l'APIRouter."""
        for method in methods:
            if method == "GET":
                self.router.get(path, name=endpoint)(view_func)
            elif method == "POST":
                self.router.post(path, name=endpoint)(view_func)
            elif method == "PUT":
                self.router.put(path, name=endpoint)(view_func)
            elif method == "DELETE":
                self.router.delete(path, name=endpoint)(view_func)

    def redirect(self, location: str, code: int = 302):
        """Redirige vers une URL spécifique."""
        return RedirectResponse(url=location, status_code=code)

    def render(self, request: Request, template_name: str, **context):
        """Rend une vue avec des variables de contexte."""
        templates = Jinja2Templates(directory="templates")
        context["request"] = request
        return templates.TemplateResponse(template_name, context)

    def flash(self, message: str, category: str = "message"):
        """Ajoute un message flash à la session."""
        # FastAPI ne supporte pas nativement les messages flash comme Flask.
        # Vous pouvez implémenter une solution personnalisée si nécessaire.
        pass

    def json(self, data: dict, status: int = 200):
        """Renvoie une réponse JSON."""
        return JSONResponse(content=data, status_code=status)
