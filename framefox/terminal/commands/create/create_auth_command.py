import os

from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.class_name_manager import ClassNameManager
from framefox.terminal.common.file_creator import FileCreator
from framefox.terminal.common.input_manager import InputManager
from framefox.terminal.common.model_checker import ModelChecker
from framefox.terminal.common.security_configurator import SecurityConfigurator

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen & LEUROND Raphael
Github: https://github.com/RayenBou
Github: https://github.com/Vasulvius
"""


class CreateAuthCommand(AbstractCommand):
    def __init__(self):
        super().__init__()
        self.default_template_name = r"security/default_authenticator_template.jinja2"
        self.custom_template_name = r"security/custom_authenticator_template.jinja2"
        self.login_controller_template_name = (
            r"security/login_controller_template.jinja2"
        )
        self.login_view_template_name = r"security/login_view_template.jinja2"
        self.authenticator_path = r"src/security"
        self.controller_path = r"src/controllers"
        self.view_path = r"templates/security"
        os.makedirs(self.view_path, exist_ok=True)

    def execute(self):
        auth_type = self._ask_authenticator_type()
        auth_name = self._ask_authenticator_name(auth_type)
        provider_name = None
        if auth_type == "custom":
            use_provider = InputManager().wait_input(
                "Do you want to add a provider to this custom authenticator?",
                choices=["yes", "no"],
                default="no",
            )
            if use_provider.lower() == "yes":
                provider_name = self._get_and_validate_provider()
                if not provider_name:
                    return
        else:
            provider_name = self._get_and_validate_provider()
            if not provider_name:
                return

        authenticator_import_path = self._create_login_files(auth_type, auth_name)
        self._configure_security(
            provider_name, authenticator_import_path, auth_type, auth_name
        )

    def _ask_authenticator_type(self) -> str:
        self.printer.print_msg(
            "Choose an authenticator type",
            theme="bold_normal",
            linebefore=True,
        )
        while True:
            print("")

            self.printer.print_msg(
                "1.[bold orange1] Default authenticator[/bold orange1]",
                theme="normal",
            )
            self.printer.print_msg(
                "2.[bold orange1] Custom authenticator[/bold orange1]",
                theme="normal",
                newline=True,
            )

            user_choice = InputManager().wait_input(
                "Authenticator type", choices=["1", "2"], default="1"
            )

            return "custom" if user_choice == "2" else "default"

    def _ask_authenticator_name(self, auth_type: str) -> str:
        default_name = "custom" if auth_type == "custom" else "default"

        while True:
            self.printer.print_msg(
                f"Choose a name for your {
                    auth_type} authenticator [default: {default_name}]",
                theme="bold_normal",
                linebefore=True,
            )
            user_name = InputManager().wait_input(
                "Authenticator name(snake_case)", default=default_name
            )
            name = user_name.strip() if user_name.strip() else default_name

            if not ClassNameManager.is_snake_case(name):
                self.printer.print_msg(
                    "Invalid authenticator name. Must be in snake_case.",
                    theme="error",
                    linebefore=True,
                    newline=True,
                )
                continue

            return name

    def _get_and_validate_provider(self):
        while True:
            self.printer.print_msg(
                "What is the name of the entity that will be used as the provider?",
                theme="bold_normal",
                linebefore=True,
            )
            provider_name = InputManager().wait_input("Provider name", default="user")

            if self._validate_provider(provider_name):
                return provider_name
            else:
                continue

    def _create_login_files(self, auth_type: str, auth_name: str) -> str:
        class_name = ClassNameManager.snake_to_pascal(auth_name)
        file_name = f"{auth_name.lower()}_authenticator"
        auth_path = os.path.join("src/security", f"{file_name}.py")

        # Vérifier l'existence de l'authenticator dans tous les cas
        if os.path.exists(auth_path):
            self.printer.print_full_text(
                f"[bold red]Cannot create authenticator. File already exists:[/bold red]",
                linebefore=True,
            )
            self.printer.print_msg(f"• Authenticator ({auth_path})", theme="error")
            return None

        if auth_type == "default":
            # Vérifier l'existence des fichiers supplémentaires pour default
            controller_path = os.path.join("src/controllers", "login_controller.py")
            view_path = os.path.join("templates/security", "login.html")

            existing_files = []
            if os.path.exists(controller_path):
                existing_files.append("Login controller")
            if os.path.exists(view_path):
                existing_files.append("Login view")

            if existing_files:
                self.printer.print_full_text(
                    f"[bold red]Cannot create login files. Following files already exist:[/bold red]",
                    linebefore=True,
                )
                for file in existing_files:
                    self.printer.print_msg(f"• {file}", theme="error")
                return None

            file_path = FileCreator().create_file(
                self.login_controller_template_name,
                self.controller_path,
                name="login_controller",
                data={},
            )
            self.printer.print_full_text(
                f"[bold orange1]Login controller created successfully:[/bold orange1] {
                    file_path}",
                linebefore=True,
            )

            file_path = FileCreator().create_file(
                self.login_view_template_name,
                self.view_path,
                name="login.html",
                data={},
                format="html",
            )
            self.printer.print_full_text(
                f"[bold orange1]Login view created successfully:[/bold orange1] {
                    file_path}",
            )
            file_path = FileCreator().create_file(
                self.default_template_name,
                self.authenticator_path,
                name=file_name,
                data={"authenticator_name": class_name},
            )
            self.printer.print_full_text(
                f"[bold orange1]Form login authenticator created successfully:[/bold orange1] {
                    file_path}",
                linebefore=True,
            )
        else:
            file_path = FileCreator().create_file(
                self.custom_template_name,
                self.authenticator_path,
                name=file_name,
                data={"authenticator_name": class_name},
            )
            self.printer.print_full_text(
                f"[bold orange1]Custom authenticator created successfully:[/bold orange1] {
                    file_path}",
                linebefore=True,
            )

        authenticator_import_path = f"src.security.{
            file_name}.{class_name}Authenticator"
        return authenticator_import_path

    def _validate_provider(self, provider_name: str) -> bool:

        if not ClassNameManager.is_snake_case(provider_name):
            self.printer.print_msg(
                "Invalid provider name. Must be in snake_case.",
                theme="error",
                linebefore=True,
                newline=True,
            )
            return False

        if not ModelChecker().check_entity_and_repository(provider_name):
            self.printer.print_msg(
                "Provider entity does not exist.",
                theme="error",
                linebefore=True,
                newline=True,
            )
            return False

        if not ModelChecker().check_entity_properties(
            provider_name, ["password", "email"]
        ):
            self.printer.print_msg(
                "Provider entity must have 'password' and 'email' properties.",
                theme="error",
                linebefore=True,
                newline=True,
            )
            return False

        return True

    def _configure_security(
        self,
        provider_name: str,
        authenticator_import_path: str,
        auth_type: str,
        auth_name: str,
    ):
        if auth_type == "default":
            provider_class = ClassNameManager.snake_to_pascal(provider_name)
            SecurityConfigurator().add_provider(provider_name, provider_class)
            SecurityConfigurator().add_firewall(
                provider_name, authenticator_import_path
            )
        else:
            provider_key = None
            if provider_name:
                provider_class = ClassNameManager.snake_to_pascal(provider_name)
                SecurityConfigurator().add_provider(provider_name, provider_class)
                provider_key = f"app_{provider_name}_provider"
            SecurityConfigurator().add_named_firewall(
                firewall_name=auth_name.lower(),
                authenticator_import_path=authenticator_import_path,
                provider_key=provider_key,
            )

        self.printer.print_full_text(
            "[bold orange1]Manage your Access control in[/bold orange1] config/security.yaml [bold orange1]to add permissions.[/bold orange1]",
            newline=True,
        )
