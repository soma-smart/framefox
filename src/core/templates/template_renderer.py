from jinja2 import Environment, FileSystemLoader

from src.core.config.settings import Settings
from injectable import Autowired, injectable, autowired
from typing import Annotated


@injectable
class TemplateRenderer:
    @autowired
    def __init__(self, settings: Annotated[Settings, Autowired]):
        self.template_dir = settings.template_dir
        self.env = Environment(loader=FileSystemLoader(self.template_dir))

    def render(self, template_name: str, context: dict = {}) -> str:
        template = self.env.get_template(template_name)
        return template.render(**context)
