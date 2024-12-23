from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse

from src.core.request.request_stack import RequestStack
from src.core.request.session.session import Session

from injectable import Autowired, autowired
from typing import Annotated
from src.core.orm.entity_manager import EntityManager


class AbstractController:
    @autowired
    def __init__(self, entity_manager: Annotated[EntityManager, Autowired]):
        self.router = APIRouter()
        self.entity_manager = entity_manager

    def redirect(self, location: str, code: int = 302):
        """Redirects to a specific URL."""
        return RedirectResponse(url=location, status_code=code)

    def flash(self, category: str, message: str):
        """Adds a flash message to the session."""
        flash_messages = Session.get("flash_messages", [])
        flash_messages.append({"message": message, "category": category})
        Session.set("flash_messages", flash_messages)

    def render(self, template_name: str, context_list: list):
        """Renders a view with context variables."""
        templates = Jinja2Templates(directory="templates")
        context = dict(context_list)
        request = RequestStack.get_request()
        context["request"] = request
        if Session.has("flash_messages"):
            context["messages"] = Session.get("flash_messages")
            Session.remove("flash_messages")
        return templates.TemplateResponse(template_name, context)

    def json(self, data: dict, status: int = 200):
        """Returns a JSON response."""
        return JSONResponse(content=data, status_code=status)
