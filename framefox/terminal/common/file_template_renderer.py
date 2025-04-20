import importlib.resources as pkg_resources
import os

from jinja2 import Environment, FileSystemLoader

import framefox.terminal


TEMPLATE_PATH = pkg_resources.files(framefox.terminal).joinpath("templates")


class FileTemplateRenderer:
    @staticmethod
    def create_file(
        template: str, output_path: str, data: dict = {}
    ):
        """
        Create a file using a template.

        Args:
            template (str): The name of the template file.
            output_path (str): The output path where the file will be created.
            data (str): The data to be rendered in the template.
        """
        env = Environment(loader=FileSystemLoader(TEMPLATE_PATH))
        template = env.get_template(template)
        code = template.render(data)

        with open(output_path, "w") as file:
            file.write(code)

    @staticmethod
    def check_if_exists(output_path: str) -> bool:
        """Check if a file already exists"""
        return os.path.exists(output_path)
