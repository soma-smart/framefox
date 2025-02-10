from framefox.core.di.service_container import ServiceContainer
from framefox.core.security.password.password_hasher import PasswordHasher
from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.input_manager import InputManager


class CreateHashCommand(AbstractCommand):
    def __init__(self):
        super().__init__("hash")

        self.password_hasher = PasswordHasher()

    def execute(self):
        """
        Hash a password and display the result
        """
        self.printer.print_msg(
            "Enter the password to hash:",
            theme="bold_normal",
            linebefore=True,
        )
        password = InputManager().wait_input("Password")

        if not password:
            self.printer.print_msg(
                "Password cannot be empty",
                theme="error",
                linebefore=True,
            )
            return

        hashed_password = self.password_hasher.hash(password)

        self.printer.print_full_text(
            f"[bold orange1]Hashed password:[/bold orange1] {hashed_password}",
            linebefore=True,
        )
        print("")
