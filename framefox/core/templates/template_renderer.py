from jinja2 import Environment, FileSystemLoader
from pathlib import Path

from framefox.core.config.settings import Settings
from framefox.core.di.service_container import ServiceContainer


class TemplateRenderer:

    def __init__(self):
        self.container = ServiceContainer()
        self.settings = self.container.get(Settings)
        self.user_template_dir = self.settings.template_dir
        self.framework_template_dir = Path(__file__).parent / "views"
        self.env = Environment(
            loader=FileSystemLoader(
                [self.user_template_dir, str(self.framework_template_dir)]
            )
        )

    def render(self, template_name: str, context: dict = {}) -> str:
        template = self.env.get_template(template_name)
        return template.render(**context)
