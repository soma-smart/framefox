"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""

import os
import re
from pathlib import Path
import yaml
from dotenv import load_dotenv

env_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path=env_path)

ENV_VAR_PATTERN = re.compile(r"\$\{(\w+)\}")

#APP_ENV = os.getenv("APP_ENV", "prod")

class Settings:
    """
    Settings class for loading and managing application configuration.
    
    Attributes:
        app_env (str): The application environment, default is 'prod'.
        config (dict): Dictionary to store the loaded configuration.
    """

    def __init__(self):
        """ 
        Initializes the Settings object and loads configurations from the specified folder. 
        
        Raises:
            Exception: If the configuration files cannot be loaded.
        """
        if os.path.exists(env_path):
            load_dotenv(dotenv_path=env_path, override=True)
        else:
            print(f"WARNING: .env file not found!")
        self.app_env = os.getenv("APP_ENV", "prod")
        self.config = {}
        try:
            self.load_configs("./config")
        except FileNotFoundError as e:
            raise Exception("Unable to load configuration") from e

    def load_configs(self, config_folder):
        """
        Loads configuration files from the specified folder and merges them into the config attribute.
        
        Args:
            config_folder (str): The path to the folder containing the configuration files.
        
        Raises:
            FileNotFoundError: If the configuration folder does not exist.
        """
        config_path = Path(config_folder).resolve()
        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"""Configuration file '{
                    config_folder}' does not exist"""
            )

        for filename in os.listdir(config_path):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                file_path = os.path.join(config_path, filename)
                with open(file_path, "r") as file:
                    config_data = yaml.safe_load(file)
                    config_data = self.replace_env_variables(config_data)
                    self.merge_dicts(self.config, config_data)

    def merge_dicts(self, base, new):
        """ 
        Recursively merges two dictionaries. 
        
        Args:
            base: The base dictionary to merge into.
            new: The new dictionary to merge.
        
        Returns:
            The merged dictionary.
        """
        for key, value in new.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self.merge_dicts(base[key], value)
            else:
                base[key] = value

    def replace_env_variables(self, data):
        """ 
        Recursively replaces environment variable placeholders in the configuration data with their actual values. 
        
        Args:
            data: The configuration data to process.
        
        Returns:
            The configuration data with environment variables replaced by their values.
        """
        if isinstance(data, dict):
            return {k: self.replace_env_variables(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.replace_env_variables(element) for element in data]
        elif isinstance(data, str):
            return ENV_VAR_PATTERN.sub(self.get_env_variable, data)
        else:
            return data

    def get_env_variable(self, match):
        """ 
        Retrieves the value of an environment variable given a regex match object.

        Args:
            match (re.Match): A regex match object containing the environment variable name.
        
        Returns:
            The value of the environment variable or an empty string if the variable does not exist.
        """
        var_name = match.group(1)
        value = os.getenv(var_name, "")
        return value

    def get_param(self, param_path: str, default=None):
        """
        Retrieves a custom parameter from the configuration using dot notation.

        Args:
            param_path (str): Path of the parameter in dot notation (e.g., 'custom_variables.api_key')
            default: Default value to return if the parameter does not exist

        Returns:
            The value of the parameter or the default value if the parameter does not exist
        """
        try:
            current = self.config.get("parameters", {})
            for key in param_path.split("."):
                if isinstance(current, dict):
                    current = current.get(key)
                else:
                    return default
                if current is None:
                    return default
            return current
        except Exception:
            return default

    # ------------------------------ cache ------------------------------

    @property
    def cache_dir(self):
        """ Returns the cache directory from the configuration. """
        cache_path = os.path.join(os.path.dirname(__file__), "../../../var/cache")
        os.makedirs(cache_path, exist_ok=True)
        return cache_path

    # ------------------------------ database ------------------------------

    @property
    def database_url(self):
        """ Returns the database URI from the configuration, default is 'sqlite:///app.db'. """
        return self.config.get("database", {}).get("url")

    @property
    def database_echo(self):
        """ Returns True if the application environment is 'dev', otherwise False. """
        return self.app_env == "dev"

    @property
    def orm_config(self):
        """ Returns the ORM configuration from the configuration. """
        return self.config.get("database", {})

    # ------------------------------ security ------------------------------

    @property
    def access_control(self):
        """ Returns the access control configuration from the configuration. """
        return self.config.get("security", {}).get("access_control", [])

    @property
    def firewalls(self):
        """ Returns the firewalls configuration from the configuration. """
        return self.config.get("security", {}).get("firewalls", {})

    def get_firewall_config(self, firewall_name: str):
        """ Returns the configuration for a specific firewall. """
        firewalls = self.firewalls
        return firewalls.get(firewall_name, {})

    @property
    def providers(self):
        """ Returns the security providers configuration from the configuration. """
        return self.config.get("security", {}).get("providers", {})

    # ------------------------------ session ------------------------------

    @property
    def cookie_secret_key(self):
        """ Returns the session secret key from the configuration, default"""
        return self.config.get("cookie", {}).get("secret_key", "default_secret")

    @property
    def cookie_type(self):
        """ Returns the session type from the configuration, default is 'filesystem'. """
        return self.config.get("cookie", {}).get("type", "filesystem")

    @property
    def cookie_max_age(self):
        """ Returns the session max age from the configuration, default is 3600 seconds. """
        return self.config.get("cookie", {}).get("max_age", 3600)

    @property
    def cookie_same_site(self):
        """ Returns the session same site policy from the configuration, default is 'lax'. """
        return self.config.get("cookie", {}).get("same_site", "lax")

    @property
    def cookie_secure(self):
        """ Returns True if sessions are HTTPS only, otherwise False. """
        return self.config.get("cookie", {}).get("secure", True)

    @property
    def cookie_http_only(self):
        """ Returns True if sessions are HTTP only, otherwise False. """
        return self.config.get("cookie", {}).get("http_only", True)

    @property
    def cookie_path(self):
        """ Returns the session cookie path from the configuration, default is '/'. """
        return self.config.get("cookie", {}).get("path", "/")

    # ------------------------------ application ------------------------------
    @property
    def openapi_url(self):
        """ Returns the OpenAPI URL from the configuration. """
        if self.app_env == "dev":
            return self.config.get("application", {}).get("openapi_url", None)
        return None

    @property
    def redoc_url(self):
        """ Returns the ReDoc URL from the configuration. """
        if self.app_env == "dev":
            return self.config.get("application", {}).get("redoc_url", None)
        return None

    @property
    def controller_dir(self):
        """ Returns the controllers directory from the configuration. """
        return (
            self.config.get("application", {})
            .get("controllers")
            .get("dir", "controllers")
        )

    @property
    def cors_config(self):
        """ Returns the CORS configuration from the configuration. """
        return self.config.get("application", {}).get("cors", {})

    @property
    def debug_mode(self):
        """ Returns True if the application environment is 'dev', otherwise False. """
        return self.app_env == "dev"

    @property
    def template_dir(self):
        """ Returns the template directory from the configuration. """
        return self.config.get("application", {}).get("template_dir", "templates")

    @property
    def session_cookie_name(self):
        """ Returns the session cookie name from the configuration. """
        return self.config.get("application", {}).get("session").get("name", None)

    @property
    def session_file_path(self):
        """ Returns the session file path from the configuration. """
        return self.config.get("application", {}).get("session").get("file_path", None)
