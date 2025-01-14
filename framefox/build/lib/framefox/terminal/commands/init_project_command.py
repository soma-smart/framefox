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
        # Create config directory
        os.makedirs(os.path.join(".", "config"))
        # Create usefull files
        # main.py
        FileCreator().create_file(
            template="init_files/main.jinja2",
            path=".",
            name="main",
            data={},
        )
        # .env
        FileCreator().create_file(
            template="init_files/env.jinja2",
            path=".",
            name=".env",
            data={},
            format="env"
        )
        # requirements.txt
        FileCreator().create_file(
            template="init_files/requirements.jinja2",
            path=".",
            name="requirements.txt",
            data={},
            format="txt"
        )
        # yaml files
        FileCreator().create_file(
            template="init_files/application.jinja2",
            path="./config",
            name="application.yaml",
            data={},
            format="yaml"
        )
        FileCreator().create_file(
            template="init_files/orm.jinja2",
            path="./config",
            name="orm.yaml",
            data={},
            format="yaml"
        )
        FileCreator().create_file(
            template="init_files/security.jinja2",
            path="./config",
            name="security.yaml",
            data={},
            format="yaml"
        )
