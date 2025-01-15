from jinja2 import Environment, FileSystemLoader

from framefox.core.config.settings import Settings
from framefox.core.di.service_container import ServiceContainer


class TemplateRenderer:

    def __init__(self):
        self.settings = ServiceContainer().get(Settings)
        self.template_dir = self.settings.template_dir
        self.env = Environment(loader=FileSystemLoader(self.template_dir))

    def render(self, template_name: str, context: dict = {}) -> str:
        template = self.env.get_template(template_name)
        return template.render(**context)
