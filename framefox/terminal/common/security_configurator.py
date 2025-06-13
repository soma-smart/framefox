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

    def add_oauth_firewall(
        self, 
        firewall_name: str, 
        authenticator_import_path: str, 
        provider_key: str = None,
        oauth_type: str = "oauth_google"
    ):
        """Add OAuth firewall configuration with OAuth-specific settings"""
        
        # Charger la configuration existante
        with open(self.yaml_path, "r") as file:
            config = self.yaml.load(file)

        if "security" not in config:
            config["security"] = {}

        if (
            "firewalls" not in config["security"]
            or config["security"]["firewalls"] is None
        ):
            config["security"]["firewalls"] = {}

        # Vérifier si le firewall existe déjà
        if firewall_name in config["security"]["firewalls"]:
            print(f"Firewall '{firewall_name}' already exists in the configuration.")
            return

        # Déterminer les variables d'environnement selon le type OAuth
        if oauth_type == "oauth_google":
            client_id_var = "GOOGLE_CLIENT_ID"
            client_secret_var = "GOOGLE_CLIENT_SECRET"
            callback_path = "/google-callback"
            oauth_config = {
                "client_id": f"${{{client_id_var}}}",
                "client_secret": f"${{{client_secret_var}}}",
                "callback_path": callback_path,
                "redirect_uri": f"${{APP_URL}}{callback_path}"
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
                "redirect_uri": f"${{APP_URL}}{callback_path}"
            }
        else:
            client_id_var = "OAUTH_CLIENT_ID"
            client_secret_var = "OAUTH_CLIENT_SECRET"
            callback_path = "/oauth-callback"
            oauth_config = {
                "client_id": f"${{{client_id_var}}}",
                "client_secret": f"${{{client_secret_var}}}",
                "callback_path": callback_path,
                "redirect_uri": f"${{APP_URL}}{callback_path}"
            }
        
        # CORRECTION: Ordre des clés - provider en premier
        firewall_config = {}
        
        # 1. Provider en premier (si défini)
        if provider_key:
            firewall_config["provider"] = provider_key
            
        # 2. Authenticator
        firewall_config["authenticator"] = authenticator_import_path
        
        # 3. Paths
        firewall_config["login_path"] = "/auth/oauth"
        firewall_config["logout_path"] = "/logout"
        firewall_config["denied_redirect"] = "/"
        
        # 4. Configuration OAuth en dernier
        firewall_config["oauth"] = oauth_config

        # Ajouter le firewall à la configuration
        config["security"]["firewalls"][firewall_name] = firewall_config
        
        # Sauvegarder la configuration
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
        
        # Charger la configuration existante
        with open(self.yaml_path, "r") as file:
            config = self.yaml.load(file)

        if "security" not in config:
            config["security"] = {}

        if (
            "firewalls" not in config["security"]
            or config["security"]["firewalls"] is None
        ):
            config["security"]["firewalls"] = {}

        # Vérifier si le firewall existe déjà
        if firewall_name in config["security"]["firewalls"]:
            print(f"Firewall '{firewall_name}' already exists in the configuration.")
            return

        # CORRECTION: Ordre des clés - provider en premier pour JWT aussi
        firewall_config = {}
        
        # 1. Provider en premier (si défini)
        if provider_key:
            firewall_config["provider"] = provider_key
            
        # 2. Authenticator
        firewall_config["authenticator"] = authenticator_import_path
        
        # 3. Pattern et logout_path
        firewall_config["pattern"] = "^/api/(users|products|auth/me|admin)"
        firewall_config["logout_path"] = "/api/auth/logout"

        # Ajouter le firewall à la configuration
        config["security"]["firewalls"][firewall_name] = firewall_config
        
        # Sauvegarder la configuration
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

        if (
            "firewalls" not in config["security"]
            or config["security"]["firewalls"] is None
        ):
            config["security"]["firewalls"] = {}

        if firewall_name in config["security"]["firewalls"]:
            print(f"Firewall '{firewall_name}' already exists in the configuration.")
        else:
            # CORRECTION: Ordre des clés - provider en premier
            new_firewall = {}
            
            # 1. Provider en premier (si défini)
            if provider_key:
                new_firewall["provider"] = provider_key
                
            # 2. Authenticator et autres configs
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

        if (
            "firewalls" not in config["security"]
            or config["security"]["firewalls"] is None
        ):
            config["security"]["firewalls"] = {}

        firewall_key = "main"
        
        # CORRECTION: Ordre des clés - provider en premier
        main_firewall = {
            "provider": f"app_{provider_name}_provider",  # En premier
            "authenticator": authenticator_import_path,
            "login_path": "/login",
            "logout_path": "/logout",
            "denied_redirect": "/"
        }

        if firewall_key in config["security"]["firewalls"]:
            print(f"Firewall '{firewall_key}' already exists in the configuration.")
        else:
            config["security"]["firewalls"][firewall_key] = main_firewall
            with open(self.yaml_path, "w") as file:
                self.yaml.dump(config, file)
            print(f"Firewall '{firewall_key}' added successfully.")