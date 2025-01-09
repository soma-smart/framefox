from src.terminal.commands.abstract_command import AbstractCommand
from src.terminal.common.class_name_manager import ClassNameManager
from src.terminal.common.file_creator import FileCreator


class CreateControllerCommand(AbstractCommand):
    def __init__(self):
        super().__init__('create_controller')
        self.controller_path = r'src/controllers'
        self.view_path = r'templates'
        self.controller_template = r'controller_template.jinja2'
        self.view_template = r'view_template.jinja2'

    def execute(self, name: str):
        if not ClassNameManager.is_snake_case(name):
            print("\033[91mInvalid name. Must be in snake_case.\033[0m")
            return

        class_name = f"{name}Controller"
        view_name = f"{name}.html"

        data_controller = {
            "controller_class_name": class_name,
            "view_name": view_name,
            "name": name,
        }
        data_view = {
            "pascal_case_name": ClassNameManager.snake_to_pascal(name),
            "controller_class_name": class_name,
        }

        FileCreator().create_file(
            template=self.controller_template,
            path=self.controller_path,
            name=f"{name}_controller",
            data=data_controller
        )
        FileCreator().create_file(
            template=self.view_template,
            path=self.view_path,
            name=view_name,
            data=data_view,
            format="html"
        )
        print("\033[92mController and view created successfully.\033[0m")
