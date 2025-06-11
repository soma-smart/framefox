from ruamel.yaml import YAML


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

        if (
            "providers" not in config["security"]
            or config["security"]["providers"] is None
        ):
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

    def add_firewall(self, provider_name: str, authenticator_import_path: str):
        with open(self.yaml_path, "r") as file:
            config = self.yaml.load(file)

        if "security" not in config:
            config["security"] = {}

        if (
            "firewalls" not in config["security"]
            or config["security"]["firewalls"] is None
        ):
            config["security"]["firewalls"] = {}

        firewall_key = "main"
        main_firewall = {
            "provider": f"app_{provider_name}_provider",
            "authenticator": authenticator_import_path,
            "login_path": "/login",
            "logout_path": "/logout",
            "denied_redirect": "/"
        }

        if firewall_key in config["security"]["firewalls"]:
            print(
                f"Firewall '{
                  firewall_key}' already exists in the configuration."
            )
        else:
            config["security"]["firewalls"][firewall_key] = main_firewall
            with open(self.yaml_path, "w") as file:
                self.yaml.dump(config, file)
            print(f"Firewall '{firewall_key}' added successfully.")

    def add_named_firewall(
        self,
        firewall_name: str,
        authenticator_import_path: str,
        provider_key: str = None,
    ):
        with open(self.yaml_path, "r") as file:
            config = self.yaml.load(file)

        if "security" not in config:
            config["security"] = {}

        if (
            "firewalls" not in config["security"]
            or config["security"]["firewalls"] is None
        ):
            config["security"]["firewalls"] = {}

        if firewall_name in config["security"]["firewalls"]:
            print(
                f"Firewall '{
                  firewall_name}' already exists in the configuration."
            )
        else:
            new_firewall = {
                "authenticator": authenticator_import_path,
                "login_path": "/login",
                "logout_path": "/logout",
                "denied_redirect": "/"
            }
            if provider_key:
                new_firewall["provider"] = provider_key

            config["security"]["firewalls"][firewall_name] = new_firewall
            with open(self.yaml_path, "w") as file:
                self.yaml.dump(config, file)
            print(f"Firewall '{firewall_name}' added successfully.")
