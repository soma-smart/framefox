import os
from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.file_creator import FileCreator


class InitProjectCommand(AbstractCommand):
    def __init__(self):
        super().__init__('init_project')

    def execute(self):
        """
        Initializes a new project
        """
        if os.path.exists("src"):
            print("Project already exists")
            return
        else:
            InitProjectCommand.create_empty_project()
            print("Project created successfully")

    @staticmethod
    def create_empty_project():
        # Create src directory
        project_path = "src"
        os.makedirs(os.path.join(project_path, "controllers"))
        os.makedirs(os.path.join(project_path, "entity"))
        os.makedirs(os.path.join(project_path, "repository"))
        # Create templates directory
        os.makedirs(os.path.join(".", "templates"))
        # Create usefull files
        # .env, main.py, requirements.txt
        # template: str, path: str, name: str, data: str, format: str = "py"
        FileCreator().create_file(
            template="init_files/main.jinja2",
            path=".",
            name="test_main",
            data={},
        )
