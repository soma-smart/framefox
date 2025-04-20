import importlib.resources as pkg_resources
import os

from jinja2 import Environment, FileSystemLoader

import framefox.terminal


class FileCreator:
    def __init__(self):
        # self.template_path = r"framefox/framefox/terminal/templates"
        self.template_path = pkg_resources.files(framefox.terminal).joinpath(
            "templates"
        )

    def create_file(
        self, template: str, output_path: str, data: dict = {}
    ):
        """
        Create a file using a template.

        Args:
            template (str): The name of the template file.
            output_path (str): The output path where the file will be created.
            data (str): The data to be rendered in the template.
        """
        env = Environment(loader=FileSystemLoader(self.template_path))
        template = env.get_template(template)
        code = template.render(data)

        with open(output_path, "w") as file:
            file.write(code)

    def check_if_exists(self, path: str, name: str, format: str = "py") -> bool:
        """Check if a file already exists"""
        file_path = os.path.join(path, f"{name}.{format}")
        return os.path.exists(file_path)
