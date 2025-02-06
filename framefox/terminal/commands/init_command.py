import os
from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.file_creator import FileCreator


class InitCommand(AbstractCommand):
    def __init__(self):
        super().__init__("init")

    def execute(self):
        """
        Initializes a new Framefox project
        """
        if os.path.exists("src"):
            self.printer.print_msg(
                "If you want to create a new project, delete the existing project first",
                theme="warning",
                linebefore=True,
                newline=True,
            )
            return
        else:
            InitCommand.create_empty_project()
            self.printer.print_msg(
                "Project created successfully",
                theme="success",
                linebefore=True,
                newline=True,
            )
            self.printer.print_full_text(
                "Next, try [bold orange1]framefox[/bold orange1] to see the available commands",
                newline=True,
            )

    @staticmethod
    def create_empty_project():
        # Create src directorys
        project_path = "src"
        os.makedirs(os.path.join(project_path, "controllers"))
        os.makedirs(os.path.join(project_path, "entity"))
        os.makedirs(os.path.join(project_path, "repository"))
        os.makedirs(os.path.join(project_path, "security"))
        os.makedirs(os.path.join("src/security", "authenticator"))
        # Create templates directory
        os.makedirs(os.path.join(".", "templates"))
        # Create public directory
        os.makedirs(os.path.join(".", "public"))

        # Create config directory
        os.makedirs(os.path.join(".", "config"))
        # Create var directory
        os.makedirs(os.path.join(".", "var"))
        os.makedirs(os.path.join("./var", "log"))
        os.makedirs(os.path.join("./var", "session"))
        # Create migrations directory
        os.makedirs(os.path.join(".", "migrations"))
        os.makedirs(os.path.join("./migrations", "versions"))
        os.makedirs(os.path.join("./migrations", "versions", "__pycache__"))
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
            format="env",
        )
        # base.html
        FileCreator().create_file(
            template="init_files/base.jinja2",
            path="./templates",
            name="base.html",
            data={},
            format="html",
        )
        # yaml files
        FileCreator().create_file(
            template="init_files/application.jinja2",
            path="./config",
            name="application.yaml",
            data={},
            format="yaml",
        )
        FileCreator().create_file(
            template="init_files/orm.jinja2",
            path="./config",
            name="orm.yaml",
            data={},
            format="yaml",
        )
        FileCreator().create_file(
            template="init_files/security.jinja2",
            path="./config",
            name="security.yaml",
            data={},
            format="yaml",
        )
        # env.py in migrations
        FileCreator().create_file(
            template="init_files/env.py.jinja2",
            path="./migrations",
            name="env",
            data={},
            format="py",
        )
        # env.py in migrations
        FileCreator().create_file(
            template="init_files/blank.jinja2",
            path="./migrations/versions/__pycache__",
            name=".gitkeep",
            data={},
            format="gitkeep",
        )
        # gitignore
        FileCreator().create_file(
            template="init_files/gitignore.jinja2",
            path=".",
            name=".gitignore",
            data={},
            format="gitignore",
        )
