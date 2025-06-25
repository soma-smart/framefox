import importlib.resources as pkg_resources
import os

import framefox.terminal
from jinja2 import Environment, FileSystemLoader

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphael
Github: https://github.com/Vasulvius 
"""


class FileCreator:
    def __init__(self):
        # self.template_path = r"framefox/framefox/terminal/templates"
        self.template_path = pkg_resources.files(framefox.terminal).joinpath(
            "templates"
        )

    def create_file(
        self, template: str, path: str, name: str, data: str, format: str = "py"
    ):
        """
        Create a file using a template.

        Args:
            template (str): The name of the template file.
            path (str): The path where the file will be created.
            name (str): The name of the file (without extension).
            data (str): The data to be rendered in the template.
            format (str): The file format (default is "py").

        Returns:
            file_path (str): The path of the created file.
        """
        env = Environment(loader=FileSystemLoader(self.template_path))
        template = env.get_template(template)
        code = template.render(data)
        if format == "py":
            output_file = f"{path}/{name}.py"
        else:
            output_file = f"{path}/{name}"
        with open(output_file, "w") as file:
            file.write(code)

        return output_file

    def check_if_exists(self, path: str, name: str, format: str = "py") -> bool:
        """Check if a file already exists"""
        file_path = os.path.join(path, f"{name}.{format}")
        return os.path.exists(file_path)
