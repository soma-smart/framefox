import os
from typing import Dict

from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.class_name_manager import ClassNameManager
from framefox.terminal.common.env_manager import EnvManager
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
        super().__init__("auth")
        self.default_template_name = r"security/default_authenticator_template.jinja2"
        self.custom_template_name = r"security/custom_authenticator_template.jinja2"
        self.login_controller_template_name = r"security/login_controller_template.jinja2"
        self.login_view_template_name = r"security/login_view_template.jinja2"

        self.jwt_template_name = r"security/jwt_authenticator_template.jinja2"
        self.oauth_google_template_name = r"security/oauth_google_authenticator_template.jinja2"
        self.oauth_microsoft_template_name = r"security/oauth_microsoft_authenticator_template.jinja2"

        self.oauth_controller_template_name = r"security/oauth_controller_template.jinja2"
        self.jwt_controller_template_name = r"security/jwt_controller_template.jinja2"

        self.env_manager = EnvManager()

        self.authenticator_path = r"src/security"
        self.controller_path = self.get_settings().controller_dir
        self.view_path = r"templates/security"
        os.makedirs(self.view_path, exist_ok=True)

    def execute(self):
        """
        Create a new authenticator.\n
        This method handles the creation of a new authenticator based on user input.\n
        It prompts the user to select an authenticator type, name it, and optionally\n
        associate it with a provider. It then generates the necessary files and\n
        configures the security settings accordingly.\n
        Raises:\n
            Exception: If there is an issue while creating the authenticator files.\n
        """
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
        elif auth_type in ["oauth_google", "oauth_microsoft"]:
            provider_name = self._get_optional_oauth_provider()
        elif auth_type in ["form", "jwt_api"]:
            provider_name = self._get_and_validate_provider()
            if not provider_name:
                return

        authenticator_import_path = self._create_login_files(auth_type, auth_name)
        if not authenticator_import_path:
            raise Exception("Issue while creating the authenticator.")

        self._configure_security(provider_name, authenticator_import_path, auth_type, auth_name)

    def _ask_authenticator_type(self) -> str:
        self.printer.print_msg(
            "Choose an authenticator type",
            theme="bold_normal",
            linebefore=True,
        )
        print("")

        options = [
            "1. [bold orange1]Form Login[/bold orange1] (email/password web forms)",
            "2. [bold orange1]JWT API[/bold orange1] (stateless API authentication)",
            "3. [bold orange1]OAuth Google[/bold orange1] (Google Sign-In)",
            "4. [bold orange1]OAuth Microsoft[/bold orange1] (Microsoft/Azure AD)",
            "5. [bold orange1]Custom[/bold orange1] (advanced cases)",
        ]

        for option in options:
            self.printer.print_msg(option, theme="normal")

        choice = InputManager().wait_input("Authenticator type", choices=["1", "2", "3", "4", "5"], default="1")

        return {
            "1": "form",
            "2": "jwt_api",
            "3": "oauth_google",
            "4": "oauth_microsoft",
            "5": "custom",
        }[choice]

    def _ask_authenticator_name(self, auth_type: str) -> str:

        default_names = {
            "form": "default",
            "jwt_api": "jwt",
            "oauth_google": "oauth",
            "oauth_microsoft": "oauth",
            "custom": "custom",
        }

        default_name = default_names.get(auth_type, "default")

        while True:
            self.printer.print_msg(
                f"Choose a name for your {auth_type} authenticator [default: {default_name}]",
                theme="bold_normal",
                linebefore=True,
            )
            user_name = InputManager().wait_input("Authenticator name (snake_case)", default=default_name)
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

    def _validate_provider(self, provider_name: str) -> bool:

        if not ClassNameManager.is_snake_case(provider_name):
            self.printer.print_msg(
                "[bold red]Invalid provider name. Must be in snake_case.[/bold red]",
                theme="error",
                linebefore=True,
                newline=True,
            )
            return False

        if not ModelChecker().check_entity_and_repository(provider_name):
            self.printer.print_msg(
                f"[bold red]Provider entity '{provider_name}' does not exist.[/bold red]",
                theme="error",
                linebefore=True,
                newline=True,
            )
            self.printer.print_msg(
                f"[bold orange1]Create it first with:[/bold orange1] framefox create user {provider_name}",
                theme="normal",
            )
            return False

        if not ModelChecker().check_entity_properties(provider_name, ["password", "email"]):
            self.printer.print_msg(
                f"[bold red]Provider entity '{provider_name}' must have 'password' and 'email' properties.[/bold red]",
                theme="error",
                linebefore=True,
                newline=True,
            )
            return False

        return True

    def _create_login_files(self, auth_type: str, auth_name: str) -> str:
        class_name = ClassNameManager.snake_to_pascal(auth_name)
        file_name = f"{auth_name.lower()}_authenticator"
        auth_path = os.path.join("src/security", f"{file_name}.py")

        if os.path.exists(auth_path):
            self.printer.print_full_text(
                "[bold red]Cannot create authenticator. File already exists:[/bold red]",
                linebefore=True,
            )
            self.printer.print_msg(
                f"• [bold orange1]Authenticator[/bold orange1] ({auth_path})",
                theme="error",
            )

            self.printer.print_msg(
                "[bold orange1]Tip:[/bold orange1] Use a different name or delete the existing file",
                theme="normal",
                linebefore=True,
            )
            return None

        if auth_type == "form":
            return self._create_form_auth_files(class_name, file_name)
        elif auth_type == "jwt_api":
            return self._create_jwt_auth_files(class_name, file_name, auth_name)
        elif auth_type == "oauth_google":
            return self._create_oauth_google_auth_files(class_name, file_name, auth_name)
        elif auth_type == "oauth_microsoft":
            return self._create_oauth_microsoft_auth_files(class_name, file_name, auth_name)
        elif auth_type == "custom":
            return self._create_custom_auth_files(class_name, file_name)

    def _create_form_auth_files(self, class_name: str, file_name: str) -> str:
        controller_path = os.path.join(self.controller_path, "login_controller.py")
        view_path = os.path.join("templates/security", "login.html")

        existing_files = []
        if os.path.exists(controller_path):
            existing_files.append("Login controller")
        if os.path.exists(view_path):
            existing_files.append("Login view")

        if existing_files:
            self.printer.print_full_text(
                "[bold red]Cannot create login files. Following files already exist:[/bold red]",
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
            f"[bold orange1]Login controller created successfully:[/bold orange1] {file_path}",
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
            f"[bold orange1]Login view created successfully:[/bold orange1] {file_path}",
        )

        file_path = FileCreator().create_file(
            self.default_template_name,
            self.authenticator_path,
            name=file_name,
            data={"authenticator_name": class_name},
        )
        self.printer.print_full_text(
            f"[bold orange1]Form login authenticator created successfully:[/bold orange1] {file_path}",
            linebefore=True,
        )

        return f"src.security.{file_name}.{class_name}Authenticator"

    def _create_jwt_auth_files(self, class_name: str, file_name: str, auth_name: str) -> str:
        file_path = FileCreator().create_file(
            self.jwt_template_name,
            self.authenticator_path,
            name=file_name,
            data={"authenticator_name": class_name},
        )
        self.printer.print_full_text(
            f"[bold orange1]JWT API authenticator created successfully:[/bold orange1] {file_path}",
            linebefore=True,
        )

        self._add_env_variables("jwt_api")

        self._propose_jwt_controller_creation(auth_name)

        self.printer.print_full_text(
            "[bold yellow]📋 JWT Configuration:[/bold yellow]",
            linebefore=True,
        )
        self.printer.print_msg("• Environment variables added to .env file", theme="normal")
        self.printer.print_msg("• JWT parameters added to config/parameter.yaml", theme="normal")
        self.printer.print_msg("• Configure JWT token generation in your application", theme="normal")

        return f"src.security.{file_name}.{class_name}Authenticator"

    def _create_oauth_google_auth_files(self, class_name: str, file_name: str, auth_name: str) -> str:
        file_path = FileCreator().create_file(
            self.oauth_google_template_name,
            self.authenticator_path,
            name=file_name,
            data={"authenticator_name": class_name},
        )
        self.printer.print_full_text(
            f"[bold orange1]OAuth Google authenticator created successfully:[/bold orange1] {file_path}",
            linebefore=True,
        )

        self._add_env_variables("oauth_google")

        self._propose_oauth_controller_creation("google", auth_name)

        self.printer.print_full_text(
            "[bold yellow]📋 Google OAuth Configuration:[/bold yellow]",
            linebefore=True,
        )
        self.printer.print_msg("• Environment variables added to .env file", theme="normal")
        self.printer.print_msg(
            "• Update the values in .env with your Google OAuth credentials",
            theme="normal",
        )
        self.printer.print_msg(
            "• Configure Google OAuth at: https://console.developers.google.com",
            theme="normal",
        )

        return f"src.security.{file_name}.{class_name}Authenticator"

    def _create_oauth_microsoft_auth_files(self, class_name: str, file_name: str, auth_name: str) -> str:
        file_path = FileCreator().create_file(
            self.oauth_microsoft_template_name,
            self.authenticator_path,
            name=file_name,
            data={"authenticator_name": class_name},
        )
        self.printer.print_full_text(
            f"[bold orange1]OAuth Microsoft authenticator created successfully:[/bold orange1] {file_path}",
            linebefore=True,
        )

        self._add_env_variables("oauth_microsoft")
        self._propose_oauth_controller_creation("microsoft", auth_name)
        self.printer.print_full_text(
            "[bold yellow]📋 Microsoft OAuth Configuration:[/bold yellow]",
            linebefore=True,
        )
        self.printer.print_msg("• Environment variables added to .env file", theme="normal")
        self.printer.print_msg(
            "• Update the values in .env with your Microsoft OAuth credentials",
            theme="normal",
        )
        self.printer.print_msg("• Configure Microsoft App at: https://portal.azure.com", theme="normal")

        return f"src.security.{file_name}.{class_name}Authenticator"

    def _create_custom_auth_files(self, class_name: str, file_name: str) -> str:
        file_path = FileCreator().create_file(
            self.custom_template_name,
            self.authenticator_path,
            name=file_name,
            data={"authenticator_name": class_name},
        )
        self.printer.print_full_text(
            f"[bold orange1]Custom authenticator created successfully:[/bold orange1] {file_path}",
            linebefore=True,
        )

        return f"src.security.{file_name}.{class_name}Authenticator"

    def _configure_security(
        self,
        provider_name: str,
        authenticator_import_path: str,
        auth_type: str,
        auth_name: str,
    ):
        if auth_type == "form":
            provider_class = ClassNameManager.snake_to_pascal(provider_name)
            SecurityConfigurator().add_provider(provider_name, provider_class)
            SecurityConfigurator().add_firewall(provider_name, authenticator_import_path)
        elif auth_type in ["oauth_google", "oauth_microsoft"]:
            provider_class = ClassNameManager.snake_to_pascal(provider_name) if provider_name else None
            if provider_name:
                SecurityConfigurator().add_provider(provider_name, provider_class)
                provider_key = f"app_{provider_name}_provider"
            else:
                provider_key = None

            SecurityConfigurator().add_oauth_firewall(
                firewall_name=auth_name.lower(),
                authenticator_import_path=authenticator_import_path,
                provider_key=provider_key,
                oauth_type=auth_type,
            )
        elif auth_type == "jwt_api":
            provider_class = ClassNameManager.snake_to_pascal(provider_name) if provider_name else None
            if provider_name:
                SecurityConfigurator().add_provider(provider_name, provider_class)
                provider_key = f"app_{provider_name}_provider"
            else:
                provider_key = None

            SecurityConfigurator().add_jwt_firewall(
                firewall_name=auth_name.lower(),
                authenticator_import_path=authenticator_import_path,
                provider_key=provider_key,
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

        if auth_type == "jwt_api":
            self._add_jwt_parameters()

        self.printer.print_full_text(
            "[bold orange1]Manage your Access control in[/bold orange1] config/security.yaml [bold orange1]to add permissions.[/bold orange1]",
            newline=True,
        )

    def _add_jwt_parameters(self):
        try:
            parameter_path = "config/parameter.yaml"

            jwt_config = """
  jwt:
    secret_key: ${JWT_SECRET_KEY}
    expiration: 3600 # 1 Hour in seconds
    algorithm: HS256"""

            if os.path.exists(parameter_path):
                with open(parameter_path, "r") as f:
                    content = f.read()

                if "jwt:" not in content:
                    with open(parameter_path, "a") as f:
                        f.write(jwt_config)

                    self.printer.print_full_text("[bold green]✓ JWT configuration added to config/parameter.yaml[/bold green]")
                else:
                    self.printer.print_full_text("[bold yellow]ℹ JWT configuration already exists in config/parameter.yaml[/bold yellow]")
            else:
                with open(parameter_path, "w") as f:
                    f.write("parameters:")
                    f.write(jwt_config)

                self.printer.print_full_text("[bold green]✓ Created config/parameter.yaml with JWT configuration[/bold green]")

        except Exception as e:
            self.printer.print_msg(f"Warning: Could not update parameter.yaml: {e}", theme="warning")

    def _add_env_variables(self, auth_type: str) -> None:
        """
        Ajoute les variables d'environnement nécessaires au fichier .env

        Args:
            auth_type: Type d'authentification (oauth_google, oauth_microsoft, jwt_api)
        """
        try:
            variables = self.env_manager.get_section_variables(auth_type)
            section_title = self.env_manager.get_section_title(auth_type)

            if variables:
                new_variables = {}
                existing_variables = []

                for key, value in variables.items():
                    if self.env_manager.variable_exists(key):
                        existing_variables.append(key)
                    else:
                        new_variables[key] = value

                if new_variables:
                    self.env_manager.add_variables(new_variables, section_title)
                    self.printer.print_full_text(
                        f"[bold green]✓ Added {len(new_variables)} environment variable(s) to .env file[/bold green]",
                        linebefore=True,
                    )

                    for key in new_variables.keys():
                        self.printer.print_msg(f"  • {key}", theme="normal")

                if existing_variables:
                    self.printer.print_full_text(
                        f"[bold yellow]ℹ {len(existing_variables)} environment variable(s) already exist(s) in .env:[/bold yellow]"
                    )
                    for key in existing_variables:
                        self.printer.print_msg(f"  • {key}", theme="normal")

        except Exception as e:
            self.printer.print_full_text(
                f"[bold red]⚠ Warning: Could not update .env file: {e}[/bold red]",
                linebefore=True,
            )
            self.printer.print_msg(
                "Please add the required environment variables manually.",
                theme="normal",
            )

    def _propose_oauth_controller_creation(self, provider_type: str, auth_name: str):
        """
        Propose de créer un controller minimaliste pour OAuth

        Args:
            provider_type: Type de provider OAuth (google, microsoft)
            auth_name: Nom de l'authenticator
        """
        self.printer.print_msg(
            f"Do you want to create a minimal OAuth controller for {provider_type.title()}?",
            theme="bold_normal",
            linebefore=True,
        )

        self.printer.print_msg(
            "This will create a minimal controller with just the required routes (no templates).",
            theme="normal",
        )

        create_controller = InputManager().wait_input(
            "Create OAuth controller?",
            choices=["yes", "no"],
            default="yes",
        )

        if create_controller.lower() == "yes":
            self._create_oauth_controller(provider_type, auth_name)

    def _create_oauth_controller(self, provider_type: str, auth_name: str):
        """
        Crée un controller ultra-minimaliste pour OAuth

        Args:
            provider_type: Type de provider OAuth (google, microsoft)
            auth_name: Nom de l'authenticator (ex: "oauth", "google_auth", etc.)
        """
        controller_name = auth_name
        controller_file = f"{controller_name}_controller"
        controller_path = os.path.join(self.controller_path, f"{controller_file}.py")

        if os.path.exists(controller_path):
            self.printer.print_msg(
                f"Controller {controller_name} already exists! Skipping creation.",
                theme="warning",
                linebefore=True,
            )
            return

        callback_paths = {
            "google": "/google-callback",
            "microsoft": "/microsoft-callback",
        }

        provider_names = {"google": "Google", "microsoft": "Microsoft"}

        class_name = ClassNameManager.snake_to_pascal(auth_name) + "Controller"

        data = {
            "controller_class_name": class_name,
            "provider_type": provider_type,
            "provider_name": provider_names[provider_type],
            "login_path": "/auth/oauth",
            "callback_path": callback_paths[provider_type],
        }

        try:
            file_path = FileCreator().create_file(
                self.oauth_controller_template_name,
                self.controller_path,
                name=controller_file,
                data=data,
            )

            self.printer.print_full_text(
                f"[bold orange1]OAuth controller server startcreated successfully:[/bold orange1] {file_path}",
                linebefore=True,
            )

            self._display_oauth_routes_info(data)

        except Exception as e:
            self.printer.print_msg(
                f"Error creating OAuth controller: {e}",
                theme="error",
                linebefore=True,
            )

    def _display_oauth_routes_info(self, data: Dict):
        self.printer.print_full_text(
            "[bold yellow]📋 Created Routes:[/bold yellow]",
            linebefore=True,
        )

        self.printer.print_msg(
            f"• Login route: {data['login_path']} (triggers OAuth redirect)",
            theme="normal",
        )

        self.printer.print_msg(
            f"• Callback route: {data['callback_path']} (handles OAuth callback)",
            theme="normal",
        )

        self.printer.print_msg(
            "• No templates required - routes handled by security middleware",
            theme="normal",
        )

    def _propose_jwt_controller_creation(self, auth_name: str):
        """
        Propose de créer un controller minimaliste pour JWT

        Args:
            auth_name: Nom de l'authenticator
        """
        self.printer.print_msg(
            "Do you want to create a minimal JWT controller for API authentication?",
            theme="bold_normal",
            linebefore=True,
        )

        self.printer.print_msg(
            "This will create a basic controller with login, refresh and user info routes.",
            theme="normal",
        )

        create_controller = InputManager().wait_input(
            "Create JWT controller?",
            choices=["yes", "no"],
            default="yes",
        )

        if create_controller.lower() == "yes":
            self._create_jwt_controller(auth_name)

    def _create_jwt_controller(self, auth_name: str):
        """
        Crée un controller ultra-minimaliste pour JWT

        Args:
            auth_name: Nom de l'authenticator (ex: "jwt", "api_auth", etc.)
        """
        controller_name = auth_name
        controller_file = f"{controller_name}_controller"
        controller_path = os.path.join(self.controller_path, f"{controller_file}.py")

        if os.path.exists(controller_path):
            self.printer.print_msg(
                f"Controller {controller_name} already exists! Skipping creation.",
                theme="warning",
                linebefore=True,
            )
            return

        class_name = ClassNameManager.snake_to_pascal(auth_name) + "Controller"

        data = {
            "controller_class_name": class_name,
        }

        try:
            file_path = FileCreator().create_file(
                self.jwt_controller_template_name,
                self.controller_path,
                name=controller_file,
                data=data,
            )

            self.printer.print_full_text(
                f"[bold orange1]JWT controller created successfully:[/bold orange1] {file_path}",
                linebefore=True,
            )

            self._display_jwt_routes_info()

        except Exception as e:
            self.printer.print_msg(
                f"Error creating JWT controller: {e}",
                theme="error",
                linebefore=True,
            )

    def _display_jwt_routes_info(self):
        self.printer.print_full_text(
            "[bold yellow]📋 Created JWT Routes:[/bold yellow]",
            linebefore=True,
        )

        self.printer.print_msg(
            "• /api/auth/login (POST) - Generate JWT token",
            theme="normal",
        )

        self.printer.print_msg(
            "• /api/auth/refresh (POST) - Refresh JWT token",
            theme="normal",
        )

        self.printer.print_msg(
            "• /api/auth/me (GET) - Get current user info (protected)",
            theme="normal",
        )

    def _get_optional_oauth_provider(self) -> str:
        self.printer.print_msg(
            "Do you want to use a user provider for OAuth authentication?",
            theme="bold_normal",
            linebefore=True,
        )

        self.printer.print_msg(
            "• [bold orange1]With provider:[/bold orange1] OAuth users will be linked to existing entities",
            theme="normal",
        )

        self.printer.print_msg(
            "• [bold orange1]Without provider:[/bold orange1] Virtual OAuth users will be created (recommended)",
            theme="normal",
        )

        use_provider = InputManager().wait_input(
            "Use a provider?",
            choices=["yes", "no"],
            default="no",
        )

        if use_provider.lower() == "no":
            self.printer.print_msg(
                "[bold orange1]OAuth will use virtual users[/bold orange1] (no database persistence)",
                theme="normal",
            )
            return None

        while True:
            self.printer.print_msg(
                "What is the name of the entity that will be used as the OAuth provider?",
                theme="bold_normal",
                linebefore=True,
            )

            provider_name = InputManager().wait_input("Provider name")

            if not provider_name or not provider_name.strip():
                self.printer.print_msg(
                    "[bold red]Provider name is required when using a provider![/bold red]",
                    theme="error",
                    linebefore=True,
                )
                continue

            provider_name = provider_name.strip()

            if self._validate_provider(provider_name):
                return provider_name
            else:
                continue
