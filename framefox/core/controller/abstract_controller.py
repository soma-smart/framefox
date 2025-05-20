from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from framefox.core.di.service_container import ServiceContainer
from framefox.core.form.form_factory import FormFactory

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class AbstractController:
    def __init__(self):
        """
        Initializes a new controller.
        Child controllers can override this method
        to inject their own dependencies.
        """

        self._container = ServiceContainer()
        self.template_renderer = self._container.get_by_tag(
            "core.templates.template_renderer"
        )

    def redirect(self, location: str, code: int = 302):
        """Redirects to a specific URL."""
        return RedirectResponse(url=location, status_code=code)

    def flash(self, category: str, message: str):
        session = self._get_container().get_by_name("Session")
        flash_bag = session.get_flash_bag()
        flash_bag.add(category, message)

    def _get_container(self):
        """Access method to the container to facilitate testing."""
        from framefox.core.di.service_container import ServiceContainer

        return ServiceContainer()

    def generate_url(self, route_name: str, **params):
        router = self._get_container().get_by_name("Router")
        return router.url_path_for(route_name, **params)

    def render(self, template_path, context=None):
        """Renders a template with the provided context"""
        template_renderer = self._get_container().get_by_name("TemplateRenderer")
        self._last_rendered_template = template_path
        if context is None:
            context = {}

        if not template_renderer:
            return HTMLResponse(
                f"Template renderer not available. Template: {template_path}"
            )

        try:
            content = template_renderer.render(template_path, context)
            return HTMLResponse(content=content)
        except Exception as e:
            return HTMLResponse(
                content=f"Error rendering template: {str(e)}", status_code=500
            )

    def json(self, data: dict, status: int = 200):
        """Returns a JSON response."""
        return JSONResponse(content=data, status_code=status)

    def create_form(self, form_type_class, entity_instance):
        """
        Creates a form from a form type class and an entity instance
        """

        return FormFactory.create_form(form_type_class, entity_instance)

    def get_user(self, user_class=None):
        """
        Retrieves the currently authenticated user.
        """
        user_provider = self._get_container().get_by_name("UserProvider")
        return user_provider.get_current_user(user_class)
