from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.class_name_manager import ClassNameManager
from framefox.terminal.common.model_checker import ModelChecker
from framefox.terminal.common.input_manager import InputManager
from framefox.terminal.common.file_creator import FileCreator
from framefox.terminal.common.security_configurator import SecurityConfigurator


class CreateAuthCommand(AbstractCommand):
    def __init__(self):
        super().__init__('auth')
        self.login_form_template_name = r"security/form_login_authenticator_template.jinja2"
        self.login_controller_template_name = r"security/login_controller_template.jinja2"
        self.login_view_template_name = r"security/login_view_template.jinja2"
        self.register_controller_template_name = r"security/register_controller_template.jinja2"
        self.register_view_template_name = r"security/register_view_template.jinja2"
        self.login_form_path = r"src/security/authenticator"
        self.controller_path = r"src/controllers"
        self.view_path = r"templates"

    def execute(self):
        """
        Create authentication system with default or custom settings.
        """
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
        # Check snake_case
        if not ClassNameManager.is_snake_case(provider_name):
            self.printer.print_msg(
                "Invalid provider name. Must be in snake_case.",
                theme="error",
                linebefore=True,
                newline=True
            )
            return
        # Check if entity exists
        if not ModelChecker().check_entity_and_repository(provider_name):
            self.printer.print_msg(
                "Provider entity does not exist.",
                theme="error",
                linebefore=True,
                newline=True
            )
            return
        # Check if provider as password and email properties
        if not ModelChecker().check_entity_properties(provider_name, ["password", "email"]):
            self.printer.print_msg(
                "Provider entity must have 'password' and 'email' properties.",
                theme="error",
                linebefore=True,
                newline=True
            )
            return

        # self.printer.print_msg(
        #     "What is the redirection url?",
        #     theme="bold_normal",
        #     linebefore=True,
        # )
        # redirection_url = InputManager().wait_input(
        #     "Redirection url"
        # )

        # if not ClassNameManager.is_snake_case(redirection_url):
        #     self.printer.print_msg(
        #         "Invalid redirectton url. Must be in snake_case.",
        #         theme="error",
        #         linebefore=True,
        #         newline=True
        #     )
        #     return

        # Login controller
        file_path = FileCreator().create_file(
            self.login_controller_template_name,
            self.controller_path,
            name=r"login_controller",
            data={}
        )
        self.printer.print_full_text(
            f"[bold green]Login controller created successfully:[/bold green] {
                file_path}",
            linebefore=True,
        )

        # Login view
        file_path = FileCreator().create_file(
            self.login_view_template_name,
            self.view_path,
            name=r"login.html",
            data={},
            format="html",
        )
        self.printer.print_full_text(
            f"[bold green]Login view created successfully:[/bold green] {
                file_path}",
        )

        # Register controller
        file_path = FileCreator().create_file(
            self.register_controller_template_name,
            self.controller_path,
            name=r"register_controller",
            data={
                'entity_file_name': provider_name,
                'entity_class_name': ClassNameManager.snake_to_pascal(provider_name),
            }
        )
        self.printer.print_full_text(
            f"[bold green]Register controller created successfully:[/bold green] {
                file_path}",
            linebefore=True,
        )

        # Register view
        file_path = FileCreator().create_file(
            self.register_view_template_name,
            self.view_path,
            name=r"register.html",
            data={},
            format="html",
        )
        self.printer.print_full_text(
            f"[bold green]Register view created successfully:[/bold green] {
                file_path}",
        )

        # Create src/security/form_login_authenticator.py
        file_path = FileCreator().create_file(
            self.login_form_template_name,
            self.login_form_path,
            name=r"form_login_authenticator",
            data={}
        )
        self.printer.print_full_text(
            f"[bold green]Form login authenticator created successfully:[/bold green] {
                file_path}",
        )
        # Ajouter les modifications dans security.yaml
        provider_class = ClassNameManager.snake_to_pascal(provider_name)
        SecurityConfigurator().add_provider(provider_name, provider_class)
        SecurityConfigurator().add_firewall(provider_name)

        self.printer.print_full_text(
            "[bold green]Access control to[/bold green] config/security.yaml [bold green]to manage your app and permissions[/bold green]",
            newline=True,
        )
