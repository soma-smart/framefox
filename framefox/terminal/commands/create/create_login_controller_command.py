import os
from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.file_creator import FileCreator


class CreateLoginControllerCommand(AbstractCommand):
    def __init__(self):
        super().__init__('login-controller')

    def execute(self):
        """
        Create the login controller.
        """
        file_path = FileCreator().create_file(
            template="login_controller_template.jinja2",
            path=r"src/controllers",
            name="login_controller",
            data={},
        )

        self.printer.print_full_text(
            f"[bold green]Login controller created successfully:[/bold green] {
                file_path}",
            linebefore=True,
            newline=True,
        )
