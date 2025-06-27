from ruamel.yaml import YAML

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphael
Github: https://github.com/Vasulvius
"""


class SecurityConfigurator:
    def __init__(self):
        self.yaml_path = r"config/security.yaml"
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=4, offset=2)

    def add_provider(self, provider_name: str, provider_class: str):
        with open(self.yaml_path, "r") as file:
            config = self.yaml.load(file)

        if "security" not in config:
            config["security"] = {}

        if "providers" not in config["security"] or config["security"]["providers"] is None:
            config["security"]["providers"] = {}

        provider_key = f"app_{provider_name}_provider"
        new_provider = {
            "entity": {
                "class": f"src.entity.{provider_name}.{provider_class}",
                "property": "email",
            }
        }

        if provider_key in config["security"]["providers"]:
            print(f"Provider '{provider_key}' already exists in the configuration.")
        else:
            config["security"]["providers"][provider_key] = new_provider
            with open(self.yaml_path, "w") as file:
                self.yaml.dump(config, file)
            print(f"Provider '{provider_key}' added successfully.")

    def add_oauth_firewall(
        self,
        firewall_name: str,
        authenticator_import_path: str,
        provider_key: str = None,
        oauth_type: str = "oauth_google",
    ):
        """Add OAuth firewall configuration with OAuth-specific settings"""

        with open(self.yaml_path, "r") as file:
            config = self.yaml.load(file)

        if "security" not in config:
            config["security"] = {}

        if "firewalls" not in config["security"] or config["security"]["firewalls"] is None:
            config["security"]["firewalls"] = {}

        if firewall_name in config["security"]["firewalls"]:
            print(f"Firewall '{firewall_name}' already exists in the configuration.")
            return

        if oauth_type == "oauth_google":
            client_id_var = "GOOGLE_CLIENT_ID"
            client_secret_var = "GOOGLE_CLIENT_SECRET"
            callback_path = "/google-callback"
            oauth_config = {
                "client_id": f"${{{client_id_var}}}",
                "client_secret": f"${{{client_secret_var}}}",
                "callback_path": callback_path,
                "redirect_uri": f"${{APP_URL}}{callback_path}",
            }
        elif oauth_type == "oauth_microsoft":
            client_id_var = "MICROSOFT_CLIENT_ID"
            client_secret_var = "MICROSOFT_CLIENT_SECRET"
            tenant_id_var = "MICROSOFT_TENANT_ID"
            callback_path = "/microsoft-callback"
            oauth_config = {
                "client_id": f"${{{client_id_var}}}",
                "client_secret": f"${{{client_secret_var}}}",
                "tenant_id": f"${{{tenant_id_var}}}",
                "callback_path": callback_path,
                "redirect_uri": f"${{APP_URL}}{callback_path}",
            }
        else:
            client_id_var = "OAUTH_CLIENT_ID"
            client_secret_var = "OAUTH_CLIENT_SECRET"
            callback_path = "/oauth-callback"
            oauth_config = {
                "client_id": f"${{{client_id_var}}}",
                "client_secret": f"${{{client_secret_var}}}",
                "callback_path": callback_path,
                "redirect_uri": f"${{APP_URL}}{callback_path}",
            }

        firewall_config = {}

        if provider_key:
            firewall_config["provider"] = provider_key

        firewall_config["authenticator"] = authenticator_import_path
        firewall_config["login_path"] = "/auth/oauth"
        firewall_config["logout_path"] = "/logout"
        firewall_config["denied_redirect"] = "/"
        firewall_config["oauth"] = oauth_config

        config["security"]["firewalls"][firewall_name] = firewall_config

        with open(self.yaml_path, "w") as file:
            self.yaml.dump(config, file)

        print(f"OAuth firewall '{firewall_name}' added successfully.")

    def add_jwt_firewall(
        self,
        firewall_name: str,
        authenticator_import_path: str,
        provider_key: str = None,
    ):
        """Add JWT firewall configuration with JWT-specific settings"""

        with open(self.yaml_path, "r") as file:
            config = self.yaml.load(file)

        if "security" not in config:
            config["security"] = {}

        if "firewalls" not in config["security"] or config["security"]["firewalls"] is None:
            config["security"]["firewalls"] = {}

        if firewall_name in config["security"]["firewalls"]:
            print(f"Firewall '{firewall_name}' already exists in the configuration.")
            return

        firewall_config = {}

        if provider_key:
            firewall_config["provider"] = provider_key

        firewall_config["authenticator"] = authenticator_import_path
        firewall_config["pattern"] = "^/api/(users|products|auth/me|admin)"
        firewall_config["logout_path"] = "/api/auth/logout"

        config["security"]["firewalls"][firewall_name] = firewall_config

        with open(self.yaml_path, "w") as file:
            self.yaml.dump(config, file)

        print(f"JWT firewall '{firewall_name}' added successfully.")

    def add_named_firewall(
        self,
        firewall_name: str,
        authenticator_import_path: str,
        provider_key: str = None,
    ):
        """Add named firewall with provider first if defined"""

        with open(self.yaml_path, "r") as file:
            config = self.yaml.load(file)

        if "security" not in config:
            config["security"] = {}

        if "firewalls" not in config["security"] or config["security"]["firewalls"] is None:
            config["security"]["firewalls"] = {}

        if firewall_name in config["security"]["firewalls"]:
            print(f"Firewall '{firewall_name}' already exists in the configuration.")
        else:
            new_firewall = {}

            if provider_key:
                new_firewall["provider"] = provider_key

            new_firewall["authenticator"] = authenticator_import_path
            new_firewall["login_path"] = "/login"
            new_firewall["logout_path"] = "/logout"
            new_firewall["denied_redirect"] = "/"

            config["security"]["firewalls"][firewall_name] = new_firewall
            with open(self.yaml_path, "w") as file:
                self.yaml.dump(config, file)
            print(f"Firewall '{firewall_name}' added successfully.")

    def add_firewall(self, provider_name: str, authenticator_import_path: str):
        """Add main firewall with provider first"""

        with open(self.yaml_path, "r") as file:
            config = self.yaml.load(file)

        if "security" not in config:
            config["security"] = {}

        if "firewalls" not in config["security"] or config["security"]["firewalls"] is None:
            config["security"]["firewalls"] = {}

        firewall_key = "main"

        main_firewall = {
            "provider": f"app_{provider_name}_provider",
            "authenticator": authenticator_import_path,
            "login_path": "/login",
            "logout_path": "/logout",
            "denied_redirect": "/",
        }

        if firewall_key in config["security"]["firewalls"]:
            print(f"Firewall '{firewall_key}' already exists in the configuration.")
        else:
            config["security"]["firewalls"][firewall_key] = main_firewall
            with open(self.yaml_path, "w") as file:
                self.yaml.dump(config, file)
            print(f"Firewall '{firewall_key}' added successfully.")
