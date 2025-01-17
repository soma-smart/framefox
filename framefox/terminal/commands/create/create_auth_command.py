from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.input_manager import InputManager


class CreateAuthCommand(AbstractCommand):
    def __init__(self):
        super().__init__('auth')

    def execute(self):
        self.printer.print_msg(
            "Do you want to create a custom authentication system or use the default one? (y/n)",
            theme="bold_normal",
            linebefore=True,
        )
        answer_custom_auth = InputManager().wait_input(
            "Answer [?]",
            default="n",
            choices=["y", "n"],
        )
        if answer_custom_auth == "y":
            self.printer.print_msg(
                "Sorry but custom authentication is not yet supported.",
                theme="warning",
                linebefore=True,
                newline=True,
            )
        else:
            self.printer.print_msg(
                "Default authentication system will be used.",
                theme="warning",
                linebefore=True,
            )
            self.make_default_auth()

    def make_default_auth(self):
        self.printer.print_msg(
            "What is the name of the entity that will be used as the provider?",
            theme="bold_normal",
            linebefore=True,
        )
        provider_name = InputManager().wait_input(
            "Provider name"
        )

        # TODO
        # Check snake_case
        # Check if entity exists
        # Check if provider as password and email properties

        self.printer.print_msg(
            "What is the redirection url?",
            theme="bold_normal",
            linebefore=True,
        )
        redirection_url = InputManager().wait_input(
            "Redirection url"
        )

        # TODO
        # Check if url is valid

        # TODO
        # Create files
        # Seulement après toutes les questions on peut créer les fichiers
        # Create src/security/form_login_authenticator.py
        # Ajouter les modifications dans security.yaml
