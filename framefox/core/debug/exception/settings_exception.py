from framefox.core.debug.exception.base_exception import FramefoxException

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class SettingsException(FramefoxException):
    """Base settings exception"""

    pass


class EnvironmentVariableNotFoundError(SettingsException):
    """Raised when an environment variable referenced in configuration is not defined"""

    def __init__(self, variable_name: str, config_file: str = None, original_error=None):
        self.variable_name = variable_name
        self.config_file = config_file

        if config_file:
            message = f"Environment variable '{variable_name}' referenced in '{config_file}' is not defined. Please set it in your .env file or environment variables."
        else:
            message = f"Environment variable '{variable_name}' is not defined. Please set it in your .env file or environment variables."

        super().__init__(message, original_error, "SETTINGS_ENV_VAR_NOT_FOUND")


class ConfigurationFileNotFoundError(SettingsException):
    """Raised when a configuration file is missing"""

    def __init__(self, config_path: str, original_error=None):
        self.config_path = config_path
        message = f"Configuration file or directory not found: '{config_path}'"
        super().__init__(message, original_error, "SETTINGS_CONFIG_FILE_NOT_FOUND")


class InvalidConfigurationError(SettingsException):
    """Raised when configuration format is invalid or contains errors"""

    def __init__(self, config_file: str, reason: str = None, original_error=None):
        self.config_file = config_file
        self.reason = reason

        if reason:
            message = f"Invalid configuration in '{config_file}': {reason}"
        else:
            message = f"Invalid configuration format in '{config_file}'"

        super().__init__(message, original_error, "SETTINGS_INVALID_CONFIG")
