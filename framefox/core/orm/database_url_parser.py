from urllib.parse import urlparse

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël & BOUMAZA Rayen
Github: https://github.com/Vasulvius & https://github.com/RayenBou
"""


class DatabaseUrlParser:
    @staticmethod
    def parse_url(url: str):
        """Parse a database URL and return a configuration"""
        from framefox.core.orm.driver.database_config import DatabaseConfig

        parsed = urlparse(url)

        driver = parsed.scheme.split("+")[0]

        default_ports = {"mysql": 3306, "postgresql": 5432, "sqlite": None}

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
            port=int(parsed.port or default_ports.get(driver, 0)),
            username=parsed.username,
            password=parsed.password,
            database=parsed.path.lstrip("/"),
            charset="utf8mb4",
        )
