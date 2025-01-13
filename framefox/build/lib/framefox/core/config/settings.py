import yaml
import os
import re
from dotenv import load_dotenv
from injectable import injectable
from typing import Type, Any, Optional
import importlib

env_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path=env_path)


@injectable
class Settings:
    """
    Settings class for loading and managing application configuration.

    Attributes:
        ENV_VAR_PATTERN (re.Pattern): Regular  expression pattern to match environment variables in the format ${VAR_NAME}.
        app_env (str): The application environment, default is 'prod'.
        config (dict): Dictionary to store the loaded configuration.

    Methods:
        __init__(config_folder='../../config'):
            Initializes the Settings object and loads configurations from the specified folder.

        load_configs(config_folder):
            Loads configuration files from the specified folder and merges them into the config attribute.

        merge_dicts(base, new):
            Recursively merges two dictionaries.

        replace_env_variables(data):
            Recursively replaces environment variable placeholders in the configuration data with their actual values.

        get_env_variable(match):
            Retrieves the value of an environment variable given a regex match object.

    Properties:
        database_url (str): Returns the database URI from the configuration, default is 'sqlite:///app.db'.
        database_echo (bool): Returns True if the application environment is 'dev', otherwise False.
        orm_config (dict): Returns the ORM configuration from the configuration.
        is_auth_enabled (bool): Returns True if authentication is enabled in the configuration, otherwise False.
        access_control (list): Returns the access control configuration from the configuration.
        session_secret_key (str): Returns the session secret key from the configuration, default is 'default_secret'.
        session_type (str): Returns the session type from the configuration, default is 'filesystem'.
        session_max_age (int): Returns the session max age from the configuration, default is 3600 seconds.
        session_same_site (str): Returns the session same site policy from the configuration, default is 'lax'.
        session_https_only (bool): Returns True if sessions are HTTPS only, otherwise False.
        cors_config (dict): Returns the CORS configuration from the configuration.
        debug_mode (bool): Returns True if the application environment is 'dev', otherwise False.
    """

    ENV_VAR_PATTERN = re.compile(r"\$\{(\w+)\}")

    def __init__(self, config_folder="../config"):

        self.app_env = os.getenv("APP_ENV", "prod")

        self.config = {}
        self.load_configs(config_folder)

    def load_configs(self, config_folder):
        config_path = os.path.join(os.path.dirname(__file__), config_folder)
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
        for key, value in new.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self.merge_dicts(base[key], value)
            else:
                base[key] = value

    def replace_env_variables(self, data):
        if isinstance(data, dict):
            return {k: self.replace_env_variables(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.replace_env_variables(element) for element in data]
        elif isinstance(data, str):
            return self.ENV_VAR_PATTERN.sub(self.get_env_variable, data)
        else:
            return data

    def get_env_variable(self, match):
        var_name = match.group(1)
        value = os.getenv(var_name, "")
        return value

    # ------------------------------ cache ------------------------------

    @property
    def cache_dir(self):
        cache_path = os.path.join(
            os.path.dirname(__file__), "../../../var/cache")
        os.makedirs(cache_path, exist_ok=True)
        return cache_path

    # ------------------------------ database ------------------------------

    @property
    def database_url(self):
        return self.config.get("database", {}).get("url")

    @property
    def database_echo(self):
        return self.app_env == "dev"

    @property
    def orm_config(self):
        return self.config.get("database", {})

    # ------------------------------ security ------------------------------

    @property
    def access_control(self):
        return self.config.get("security", {}).get("access_control", [])

    @property
    def firewalls(self):
        return self.config.get("security", {}).get("firewalls", {})

    def get_firewall_config(self, firewall_name: str):
        firewalls = self.firewalls
        return firewalls.get(firewall_name, {})

    @property
    def providers(self):
        return self.config.get("security", {}).get("providers", {})

    # ------------------------------ session ------------------------------

    @property
    def cookie_secret_key(self):
        return self.config.get("cookie", {}).get("secret_key", "default_secret")

    @property
    def cookie_type(self):
        return self.config.get("cookie", {}).get("type", "filesystem")

    @property
    def cookie_max_age(self):
        return self.config.get("cookie", {}).get("max_age", 3600)

    @property
    def cookie_same_site(self):
        return self.config.get("cookie", {}).get("same_site", "lax")

    @property
    def cookie_secure(self):
        return self.config.get("cookie", {}).get("secure", True)

    @property
    def cookie_http_only(self):
        return self.config.get("cookie", {}).get("http_only", True)

    @property
    def cookie_path(self):
        return self.config.get("cookie", {}).get("path", "/")

    # ------------------------------ application ------------------------------
    @property
    def openapi_url(self):
        if self.app_env == "dev":
            return self.config.get("application", {}).get("openapi_url", None)
        return None

    @property
    def redoc_url(self):
        if self.app_env == "dev":
            return self.config.get("application", {}).get("redoc_url", None)
        return None

    @property
    def controller_dir(self):
        return (
            self.config.get("application", {})
            .get("controllers")
            .get("dir", "controllers")
        )

    @property
    def cors_config(self):
        return self.config.get("application", {}).get("cors", {})

    @property
    def debug_mode(self):
        return self.app_env == "dev"

    @property
    def template_dir(self):
        return self.config.get("application", {}).get("template_dir", "templates")

    @property
    def session_cookie_name(self):
        return self.config.get("application", {}).get("session").get("name", None)

    @property
    def session_file_path(self):
        return self.config.get("application", {}).get("session").get("file_path", None)
