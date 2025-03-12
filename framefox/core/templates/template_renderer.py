from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from framefox.core.di.service_container import ServiceContainer
from framefox.core.form.extension.form_extension import FormExtension

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class TemplateRenderer:
    def __init__(self):
        self.container = ServiceContainer()
        self.settings = self.container.get_by_name("Settings")
        self.user_template_dir = self.settings.template_dir
        self.framework_template_dir = Path(__file__).parent / "views"
        self.env = Environment(
            loader=FileSystemLoader(
                [self.user_template_dir, str(self.framework_template_dir)]
            ),
            undefined=StrictUndefined,
        )
        form_extension = FormExtension(self.env)
        self.env.globals["url_for"] = self.url_for
        self.env.globals["get_flash_messages"] = self.get_flash_messages
        self.env.globals["current_user"] = self.get_current_user

        # N'oubliez pas d'appeler la méthode pour enregistrer les filtres
        self._register_filters(self.env)

    def url_for(self, name: str, **params) -> str:
        """Generates a URL from the route name"""
        try:
            router = self.container.get_by_name("Router")
            return str(router.url_path_for(name, **params))
        except Exception as e:
            print(f"Error generating URL for route '{name}': {str(e)}")
            return "#"

    def get_flash_messages(self):
        """Retrieves flash messages from the session in template format"""
        session = self.container.get_by_name("Session")
        flash_bag = session.get_flash_bag()
        return flash_bag.get_for_template()

    def render(self, template_name: str, context: dict = {}) -> str:
        template = self.env.get_template(template_name)
        return template.render(**context)

    def _register_filters(self, env):
        """Registers custom filters for Jinja2"""
        env.filters["relation_display"] = self._relation_display_filter

    def _relation_display_filter(self, value):
        """Filter to properly display relations"""
        if value is None:
            return "None"
        elif isinstance(value, list):
            if len(value) == 0:
                return "None"
            elif hasattr(value[0], "id") and hasattr(value[0], "name"):
                return ", ".join([item.name for item in value])
            else:
                return f"{len(value)} items"
        elif hasattr(value, "id") and hasattr(value, "name"):
            return value.name
        elif hasattr(value, "id"):
            return f"ID: {value.id}"
        else:
            return str(value)

    def get_current_user(self):
        """Récupère l'utilisateur actuellement connecté pour les templates"""
        try:
            user_provider = self.container.get_by_name("UserProvider")
            return user_provider.get_current_user()
        except Exception as e:
            print(f"Error retrieving current user: {str(e)}")
            return None
