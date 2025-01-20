from ruamel.yaml import YAML


class SecurityConfigurator:
    def __init__(self):
        self.yaml_path = r"config/security.yaml"
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=4, offset=2)

    def add_provider(self, provider_name: str, provider_class: str):
        # Lire le fichier YAML existant avec ruamel.yaml
        with open(self.yaml_path, 'r') as file:
            config = self.yaml.load(file)

        # Créer la nouvelle configuration du provider
        new_provider = {
            f'app_{provider_name}_provider': {
                'entity': {
                    'class': f'src.entity.{provider_name}.f{provider_class}',
                    'property': 'email'
                }
            }
        }

        # Ajouter le nouveau provider à la configuration existante
        if 'security' not in config:
            config['security'] = {}
        if 'providers' not in config['security']:
            config['security']['providers'] = {}

        config['security']['providers'].update(new_provider)

        # Sauvegarder le fichier en préservant les commentaires
        with open(self.yaml_path, 'w') as file:
            self.yaml.dump(config, file)


#   firewalls:
#     main:
#       provider: app_<provider_name>_provider
#       authenticator: src.security.authenticator.form_login_authenticator.FormLoginAuthenticator
#       login_path: /login
#       logout_path: /logout


    def add_firewall(self, provider_name: str):
        # Lire le fichier YAML existant avec ruamel.yaml
        with open(self.yaml_path, 'r') as file:
            config = self.yaml.load(file)

        # Créer la nouvelle configuration du provider
        new_main_firewall = {
            'main': {
                'provider': f'app_{provider_name}_provider',
                'authenticator': f'src.security.authenticator.form_login_authenticator.FormLoginAuthenticator',
                'login_path': f'/login',
                'logout_path': f'/logout',
            }
        }

        # Ajouter le nouveau provider à la configuration existante
        if 'firewall' not in config:
            config['firewall'] = {}
        # Ajouter le nouveau provider à la configuration existante
        if 'security' not in config:
            config['security'] = {}
        if 'firewalls' not in config['security']:
            config['security']['firewalls'] = {}

        config['security']['firewalls'].update(new_main_firewall)

        # Sauvegarder le fichier en préservant les commentaires
        with open(self.yaml_path, 'w') as file:
            self.yaml.dump(config, file)
