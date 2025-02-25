from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from framefox.core.di.service_container import ServiceContainer

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
        session = self._get_container().get_by_name("Session")
        """Adds a flash message to the session."""
        flash_messages = session.get("flash_messages", [])
        flash_messages.append({"message": message, "category": category})
        session.set("flash_messages", flash_messages)

    def render(self, template_name: str, context: dict = {}):
        template_renderer = self._get_container().get_by_name("TemplateRenderer")
        session = self._get_container().get_by_name("Session")
        """Renders a view with context variables, including CSRF token."""
        if session.has("flash_messages"):
            context["messages"] = session.get("flash_messages")
            session.remove("flash_messages")

        content = template_renderer.render(template_name, context)
        return HTMLResponse(content=content, status_code=200, media_type="text/html")

    def json(self, data: dict, status: int = 200):
        """Returns a JSON response."""
        return JSONResponse(content=data, status_code=status)
