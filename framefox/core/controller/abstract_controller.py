from fastapi import APIRouter
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from injectable import Autowired, autowired
from typing import Annotated

from framefox.core.request.session.session import Session
from framefox.core.templates.template_renderer import TemplateRenderer
from framefox.core.orm.entity_manager import EntityManager


class AbstractController:
    @autowired
    def __init__(
        self,
        entity_manager: Annotated[EntityManager, Autowired],
        template_renderer: Annotated[TemplateRenderer, Autowired],
    ):
        self.router = APIRouter()
        self.template_renderer = template_renderer
        self.entity_manager = entity_manager

    def redirect(self, location: str, code: int = 302):
        """Redirects to a specific URL."""
        return RedirectResponse(url=location, status_code=code)

    def flash(self, category: str, message: str):
        """Adds a flash message to the session."""
        flash_messages = Session.get("flash_messages", [])
        flash_messages.append({"message": message, "category": category})
        Session.set("flash_messages", flash_messages)

    def render(self, template_name: str, context: dict):
        """Renders a view with context variables, including CSRF token."""
        if Session.has("flash_messages"):
            context["messages"] = Session.get("flash_messages")
            Session.remove("flash_messages")

        content = self.template_renderer.render(template_name, context)
        return HTMLResponse(content=content, status_code=200, media_type="text/html")

    def json(self, data: dict, status: int = 200):
        """Returns a JSON response."""
        return JSONResponse(content=data, status_code=status)
