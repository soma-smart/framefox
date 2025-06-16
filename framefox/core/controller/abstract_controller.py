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
        Initializes a new controller with dependency injection container and template renderer.
        Child controller can override this method
        to inject their own dependencies.
        """

        self._container = ServiceContainer()
        self.template_renderer = self._container.get_by_tag("core.templates.template_renderer")

    def redirect(self, location: str, code: int = 302):
        """
        Redirects the user to a specific URL with an optional HTTP status code.

        Args:
            location (str): The URL to redirect to
            code (int): HTTP status code for the redirect (default: 302)
        """
        return RedirectResponse(url=location, status_code=code)

    def flash(self, category: str, message: str):
        """
        Adds a flash message to the session for displaying on the next request.

        Args:
            category (str): The category/type of the flash message (e.g., 'success', 'error')
            message (str): The message content to display
        """
        session = self._get_container().get_by_name("Session")
        flash_bag = session.get_flash_bag()
        flash_bag.add(category, message)

    def _get_container(self):
        from framefox.core.di.service_container import ServiceContainer

        return ServiceContainer()

    def generate_url(self, route_name: str, **params):
        """
        Generates a URL for a named route with optional parameters.

        Args:
            route_name (str): The name of the route to generate URL for
            **params: Additional parameters to include in the URL

        Returns:
            str: The generated URL
        """
        router = self._get_container().get_by_name("Router")
        return router.url_path_for(route_name, **params)

    def render(self, template_path, context=None):
        """
        Renders a template file with optional context data and returns an HTML response.

        Args:
            template_path (str): Path to the template file to render
            context (dict, optional): Data to pass to the template (default: None)

        Returns:
            HTMLResponse: The rendered template as HTML response
        """
        template_renderer = self._get_container().get_by_name("TemplateRenderer")
        self._last_rendered_template = template_path
        if context is None:
            context = {}
        try:
            content = template_renderer.render(template_path, context)
            return HTMLResponse(content=content)
        except Exception as e:
            return HTMLResponse(content=str(e), status_code=500)

    def json(self, data: dict, status: int = 200):
        """
        Returns data as a JSON response with optional HTTP status code.

        Args:
            data (dict): The data to serialize as JSON
            status (int): HTTP status code for the response (default: 200)

        Returns:
            JSONResponse: The data serialized as JSON response
        """
        return JSONResponse(content=data, status_code=status)

    def create_form(self, form_type_class, entity_instance):
        """
        Creates a form instance from a form type class and binds it to an entity.

        Args:
            form_type_class: The form class to instantiate
            entity_instance: The entity object to bind to the form

        Returns:
            Form: The created form instance bound to the entity
        """

        return FormFactory.create_form(form_type_class, entity_instance)

    def get_user(self, user_class=None):
        """
        Retrieves the currently authenticated user from the user provider.

        Args:
            user_class (optional): Specific user class to cast the result to (default: None)

        Returns:
            User: The current authenticated user instance or None if not authenticated
        """
        user_provider = self._get_container().get_by_name("UserProvider")
        return user_provider.get_current_user(user_class)
