from jinja2 import Environment, FileSystemLoader


class FileCreator:
    def __init__(self):
        self.template_path = r"src/terminal/templates"

    def create_file(self, template: str, path: str, name: str, data: str):
        """
        Create a file using a template.

        Args:
            template (str): The name of the template file.
            path (str): The path where the file will be created.
            name (str): The name of the file (without extension).
            data (str): The data to be rendered in the template.

        Returns:
            None
        """
        # Load the template from a file
        env = Environment(loader=FileSystemLoader(self.template_path))
        template = env.get_template(template)

        # Render the template with the data
        code = template.render(data)

        # Write to a Python file
        output_file = f"{path}/{name}.py"
        with open(output_file, "w") as file:
            file.write(code)
