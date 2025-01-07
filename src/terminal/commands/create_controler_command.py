from src.terminal.commands.abstract_command import AbstractCommand


class CreateControlerCommand(AbstractCommand):
    def __init__(self):
        super().__init__('create_controler')
        self.controler_template = r"controler_template.jinja2"
        self.controllers_path = r'src/controllers'

    def execute(self):
        data = {
            "controller_class_name": "",
            "repository_file_name": "",
            "repository_class_name": "",
            "entity_file_name": "",
            "entity_class_name": "",
            "entities_name": "",
            "entity_name": "",
        }
