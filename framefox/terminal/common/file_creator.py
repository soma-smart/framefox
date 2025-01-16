from jinja2 import Environment, FileSystemLoader

import importlib.resources as pkg_resources
import framefox.terminal


class FileCreator:
    def __init__(self):
        # self.template_path = r"framefox/framefox/terminal/templates"
        self.template_path = pkg_resources.files(
            framefox.terminal).joinpath('templates')

    def create_file(self, template: str, path: str, name: str, data: str, format: str = "py"):
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
        # Load the template from a file
        env = Environment(loader=FileSystemLoader(self.template_path))
        # env = self.create_environment()
        # print(env.list_templates())
        template = env.get_template(template)

        # Render the template with the data
        code = template.render(data)

        # Write to a Python file
        if format == "py":
            output_file = f"{path}/{name}.py"
        else:
            output_file = f"{path}/{name}"
        with open(output_file, "w") as file:
            file.write(code)

        return output_file
