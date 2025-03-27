from urllib.parse import urlparse
from typing import Dict, Any, Optional, Union
from framefox.core.orm.driver.database_config import DatabaseConfig

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël & BOUMAZA Rayen
Github: https://github.com/Vasulvius & https://github.com/RayenBou
"""


class DatabaseUrlParser:
    @staticmethod
    def parse_url(url_or_config: Union[str, Dict[str, Any]]) -> Any:
        """
        Parse a database URL or configuration dictionary and return a DatabaseConfig object.

        Args:
            url_or_config: Either a URL string or a dictionary with database configuration

        Returns:
            DatabaseConfig object with parsed connection parameters
        """

        # If a dictionary is provided, use it directly
        if isinstance(url_or_config, dict):
            # Handle both formats: nested config or flat config
            if "url" in url_or_config and isinstance(url_or_config["url"], str):
                # If URL is provided inside the dict, parse it
                return DatabaseUrlParser.parse_url(url_or_config["url"])

            # Use the dict as direct configuration
            driver = url_or_config.get("driver", "postgresql")

            if driver == "sqlite":
                return DatabaseConfig(
                    driver="sqlite",
                    database=url_or_config.get("database", "app.db"),
                    host=None,
                    port=None,
                    username=None,
                    password=None,
                )

            # Extract values with defaults
            return DatabaseConfig(
                driver=driver,
                host=url_or_config.get("host", "localhost"),
                port=int(url_or_config.get(
                    "port", DatabaseUrlParser._get_default_port(driver))),
                username=url_or_config.get("username", ""),
                password=url_or_config.get("password", ""),
                database=url_or_config.get("database", ""),
                charset=url_or_config.get("charset", "utf8mb4"),
            )

        # Parse string URL
        parsed = urlparse(url_or_config)
        driver = parsed.scheme.split("+")[0]

        if driver == "sqlite":
            return DatabaseConfig(
                driver="sqlite",
                database=parsed.path.lstrip("/"),
                host=None,
                port=None,
                username=None,
                password=None,
            )

        return DatabaseConfig(
            driver=driver,
            host=parsed.hostname or "localhost",
            port=int(parsed.port or DatabaseUrlParser._get_default_port(driver)),
            username=parsed.username,
            password=parsed.password,
            database=parsed.path.lstrip("/"),
            charset="utf8mb4",
        )

    @staticmethod
    def _get_default_port(driver: str) -> int:
        """Get the default port number for a database driver"""
        default_ports = {"mysql": 3306, "postgresql": 5432, "sqlite": None}
        return default_ports.get(driver, 0)
