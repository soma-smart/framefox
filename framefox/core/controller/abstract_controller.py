from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from framefox.core.di.service_container import ServiceContainer
from framefox.core.request.session.session import Session

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class AbstractController:

    def _get_container(self):
        return ServiceContainer()

    def redirect(self, location: str, code: int = 302):
        """Redirects to a specific URL."""
        return RedirectResponse(url=location, status_code=code)

    def flash(self, category: str, message: str):
        """Adds a flash message to the session."""
        flash_messages = Session.get("flash_messages", [])
        flash_messages.append({"message": message, "category": category})
        Session.set("flash_messages", flash_messages)

    def render(self, template_name: str, context: dict = {}):
        template_renderer = self._get_container().get_by_name("TemplateRenderer")
        """Renders a view with context variables, including CSRF token."""
        if Session.has("flash_messages"):
            context["messages"] = Session.get("flash_messages")
            Session.remove("flash_messages")

        content = template_renderer.render(template_name, context)
        return HTMLResponse(content=content, status_code=200, media_type="text/html")

    def json(self, data: dict, status: int = 200):
        """Returns a JSON response."""
        return JSONResponse(content=data, status_code=status)
