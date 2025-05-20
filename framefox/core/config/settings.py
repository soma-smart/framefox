import os
import re
from pathlib import Path

import yaml
from dotenv import load_dotenv

from framefox.core.mail.mail_url_parser import MailUrlParser
from framefox.core.orm.database_url_parser import DatabaseUrlParser

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""

env_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path=env_path)

ENV_VAR_PATTERN = re.compile(r"\$\{(\w+)\}")


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
        """Returns the cache directory from the configuration."""
        cache_path = os.path.join(os.path.dirname(__file__), "../../../var/cache")
        os.makedirs(cache_path, exist_ok=True)
        return cache_path

    # ------------------------------ database ------------------------------

    @property
    def database_url(self):
        """
        Returns the database configuration, either from the URL in .env
        or from the detailed configuration in orm.yaml.

        Priority:
        1. DATABASE_URL environment variable
        2. Detailed configuration in orm.yaml
        3. Raise exception if both are missing
        """

        db_url = os.getenv("DATABASE_URL")
        if db_url:
            return DatabaseUrlParser.parse_url(db_url)

        db_config = self.config.get("database", {})
        if db_config:

            if "url" in db_config and not db_config["url"]:
                del db_config["url"]

            if "url" in db_config and db_config["url"]:
                return DatabaseUrlParser.parse_url(db_config["url"])

            has_required_details = all(
                key in db_config for key in ["driver", "host", "database"]
            ) or (
                "driver" in db_config
                and db_config["driver"] == "sqlite"
                and "database" in db_config
            )

            if has_required_details:

                return DatabaseUrlParser.parse_url(db_config)

        raise ValueError(
            "No database configuration found. Please set DATABASE_URL in .env file "
            "or provide detailed configuration in config/orm.yaml file."
        )

    @property
    def database_echo(self):
        """
        Returns whether SQL statements should be echoed.
        True if APP_ENV is 'dev' or if explicitly set in configuration.
        """
        # Check if explicitly configured in orm.yaml
        if "echo" in self.config.get("database", {}):
            config_value = self.config["database"]["echo"]
            # Handle string values like "true", "false" from environment variables
            if isinstance(config_value, str):
                return config_value.lower() == "true"
            return bool(config_value)

        # Default behavior based on APP_ENV
        return self.app_env == "dev"

    @property
    def orm_config(self):
        """Returns the ORM configuration from the configuration."""
        return self.config.get("database", {})

    # ------------------------------ security ------------------------------

    @property
    def access_control(self):
        """Returns the access control configuration from the configuration."""
        return self.config.get("security", {}).get("access_control", [])

    @property
    def firewalls(self):
        """Returns the firewalls configuration from the configuration."""
        return self.config.get("security", {}).get("firewalls", {})

    def get_firewall_config(self, firewall_name: str):
        """Returns the configuration for a specific firewall."""
        firewalls = self.firewalls
        return firewalls.get(firewall_name, {})

    @property
    def providers(self):
        """Returns the security providers configuration from the configuration."""
        return self.config.get("security", {}).get("providers", {})

    # ------------------------------ session ------------------------------
    @property
    def profiler_enabled(self):
        """Returns whether the profiler is enabled from configuration."""
        if self.app_env != "dev":
            return False 
        enabled_str = self.config.get("application", {}).get("profiler", {}).get("enabled", "true")

        return bool(enabled_str)
    @property
    def session_name(self):
        """Returns the session  name from the configuration."""
        return self.config.get("application", {}).get("session", {}).get("name", "session_id")

    @property
    def session_file_path(self):
        """Returns the session file path from the configuration."""
        return self.config.get("application", {}).get("session", {}).get("file_path", "var/session/sessions.db")
        
    @property
    def session_secret_key(self):
        """Returns the session secret key from the configuration."""
        secret_key = self.config.get("application", {}).get("session", {}).get("secret_key", None)
        if not secret_key or secret_key == "default_secret":
            self.logger.warning("Using default session secret key. This is insecure for production environments.")
        return secret_key or "default_secret"

    # ------------------------------ cookie ------------------------------

    @property
    def cookie_max_age(self):
        """Returns the cookie max age in seconds from the configuration, default is 3600 seconds."""
        return self.config.get("application", {}).get("cookie", {}).get("max_age", 3600)

    @property
    def cookie_same_site(self):
        """Returns the cookie same site policy from the configuration, default is 'lax'."""
        return self.config.get("application", {}).get("cookie", {}).get("same_site", "lax")

    @property
    def cookie_secure(self):
        """Returns True if cookies should only be sent over HTTPS, otherwise False."""
        return self.config.get("application", {}).get("cookie", {}).get("secure", True)

    @property
    def cookie_http_only(self):
        """Returns True if cookies should be HTTP only (not accessible via JavaScript), otherwise False."""
        return self.config.get("application", {}).get("cookie", {}).get("http_only", True)

    @property
    def cookie_path(self):
        """Returns the cookie path from the configuration, default is '/'."""
        return self.config.get("application", {}).get("cookie", {}).get("path", "/")
    # ------------------------------ application ------------------------------
    @property
    def openapi_url(self):
        """Returns the OpenAPI URL from the configuration."""
        if self.app_env == "dev":
            return self.config.get("application", {}).get("openapi_url", None)
        return None

    @property
    def redoc_url(self):
        """Returns the ReDoc URL from the configuration."""
        if self.app_env == "dev":
            return self.config.get("application", {}).get("redoc_url", None)
        return None

    @property
    def controller_dir(self):
        """Returns the controllers directory from the configuration."""
        return (
            self.config.get("application", {})
            .get("controllers")
            .get("dir", "controllers")
        )

    @property
    def cors_config(self):
        """Returns the CORS configuration from the configuration."""
        return self.config.get("application", {}).get("cors", {})

    @property
    def debug_mode(self):
        """Returns True if the application environment is 'dev', otherwise False."""
        return self.app_env == "dev"

    @property
    def template_dir(self):
        """Returns the template directory from the configuration."""
        return self.config.get("application", {}).get("template_dir", "templates")

    @property
    def session_cookie_name(self):
        """Returns the session cookie name from the configuration."""
        return self.config.get("application", {}).get("session").get("name", None)

    @property
    def session_file_path(self):
        """Returns the session file path from the configuration."""
        return self.config.get("application", {}).get("session").get("file_path", None)

    # ------------------------------ mail ------------------------------

    @property
    def mail_config(self):
        """Returns the parsed mail configuration from the URL."""
        return MailUrlParser.parse_url(self.config.get("mail", {}).get("url", ""))

    # ------------------------------ tasks ------------------------------

    @property
    def task_broker_type(self) -> str:
        """Returns the type of broker to use (database, redis, rabbitmq)"""
        return self.config.get("tasks", {}).get("type", "database")



    @property
    def task_transport_url(self) -> str:
        """Returns the transport URL for RabbitMQ"""
        return self.config.get("tasks", {}).get(
            "task_transport_url", "amqp://guest:guest@localhost:5672/%2F"
        )

    @property
    def task_worker_concurrency(self) -> int:
        """Number of simultaneous tasks"""
        return self.config.get("tasks", {}).get("worker", {}).get("concurrency", 5)

    @property
    def task_polling_interval(self) -> int:
        """Interval between checks for new tasks (seconds)"""
        return self.config.get("tasks", {}).get("worker", {}).get("polling_interval", 5)

    @property
    def task_default_queues(self) -> list:
        """Default queues"""
        return (
            self.config.get("tasks", {})
            .get("worker", {})
            .get("default_queues", ["default"])
        )

    @property
    def task_cleanup_interval(self) -> int:
        """Task cleanup interval in hours"""
        return self.config.get("tasks", {}).get("cleanup", {}).get("interval_hours", 24)

    @property
    def task_retention_days(self) -> int:
        """Number of days to retain failed tasks"""
        return self.config.get("tasks", {}).get("cleanup", {}).get("retention_days", 7)

    @property
    def task_defaults(self) -> dict:
        """Default parameters for tasks"""
        defaults = {
            "queue": "default",
            "priority": 0,
            "max_retries": 3,
            "retry_delay": 300,
        }
        return {**defaults, **self.config.get("tasks", {}).get("defaults", {})}
