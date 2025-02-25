from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from framefox.core.di.service_container import ServiceContainer

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
            )
        )
        self.env.globals["url_for"] = self._url_for

    def _url_for(self, name: str, **params) -> str:
        """Generates a URL from the route name"""
        try:
            router = self.container.get_by_name("Router")
            return str(router.url_path_for(name, **params))
        except Exception as e:
            print(f"Error generating URL for route '{name}': {str(e)}")
            return "#"

    def render(self, template_name: str, context: dict = {}) -> str:
        template = self.env.get_template(template_name)
        return template.render(**context)
