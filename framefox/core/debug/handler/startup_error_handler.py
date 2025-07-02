import sys

from framefox.core.debug.exception.settings_exception import (
    ConfigurationFileNotFoundError,
    EnvironmentVariableNotFoundError,
    InvalidConfigurationError,
    SettingsException,
)

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class StartupErrorHandler:
    """Handler for startup configuration errors"""

    @staticmethod
    def handle_configuration_error(exc: SettingsException) -> None:
        """Handle configuration errors with nice formatting"""
        print("\n" + "=" * 60)
        print("🚫 \033[91mFramefox Configuration Error\033[0m")
        print("=" * 60)

        if isinstance(exc, EnvironmentVariableNotFoundError):
            print("❌ \033[93mMissing Environment Variable\033[0m")
            print(f"   Variable: \033[96m{exc.variable_name}\033[0m")
            if exc.config_file:
                print(f"   File: \033[96m{exc.config_file}\033[0m")
            print("\n💡 \033[92mSolution:\033[0m")
            print(f"   \033[95m{exc.variable_name}=your_value_here\033[0m")

        elif isinstance(exc, ConfigurationFileNotFoundError):
            print("❌ \033[93mConfiguration Not Found\033[0m")
            print(f"   Path: \033[96m{exc.config_path}\033[0m")
            print("\n💡 \033[92mSolution:\033[0m")
            print("   Create the configuration directory with YAML files")

        elif isinstance(exc, InvalidConfigurationError):
            print("❌ \033[93mInvalid Configuration\033[0m")
            print(f"   File: \033[96m{exc.config_file}\033[0m")
            if exc.reason:
                print(f"   Issue: \033[96m{exc.reason}\033[0m")
            print("\n💡 \033[92mSolution:\033[0m")
            print("   Check YAML syntax and configuration format")

        print("=" * 60)
        print()
        sys.exit(1)
