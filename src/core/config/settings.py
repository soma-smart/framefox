
import yaml
import os


class Settings:
    """
    A class to manage application settings loaded from YAML configuration files.

    Attributes:
        config (dict): A dictionary to store the merged configuration data.

    Methods:
        __init__(config_folder='../../config'):
            Initializes the Settings instance and loads configurations from the specified folder.

        load_configs(config_folder):
            Loads and merges configuration files from the specified folder.
            Args:
                config_folder (str): The relative path to the configuration folder.
            Raises:
                FileNotFoundError: If the configuration folder does not exist.

        merge_dicts(base, new):
            Recursively merges two dictionaries.
            Args:
                base (dict): The base dictionary to merge into.
                new (dict): The new dictionary to merge from.

        is_auth_enabled:
            Checks if authentication is enabled in the configuration.
            Returns:
                bool: True if authentication is enabled, False otherwise.

        access_control:
            Retrieves the access control settings from the configuration.
            Returns:
                list: A list of access control rules.
    """

    def __init__(self, config_folder='../../config'):
        self.config = {}
        self.load_configs(config_folder)

    def load_configs(self, config_folder):
        config_path = os.path.join(os.path.dirname(__file__), config_folder)
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"The configuration folder '{
                config_folder}' does not exist.")

        for filename in os.listdir(config_path):
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                file_path = os.path.join(config_path, filename)
                with open(file_path, 'r') as file:
                    config_data = yaml.safe_load(file)
                    self.merge_dicts(self.config, config_data)

    def merge_dicts(self, base, new):
        for key, value in new.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self.merge_dicts(base[key], value)
            else:
                base[key] = value

    @property
    def is_auth_enabled(self):
        return self.config.get('security', {}).get('enabled', False)

    @property
    def access_control(self):
        return self.config.get('security', {}).get('access_control', [])
