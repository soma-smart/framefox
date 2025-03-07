from urllib.parse import urlparse


class DatabaseUrlParser:
    @staticmethod
    def parse_url(url: str):
        """Parse une URL de base de données et retourne une configuration"""
        from framefox.core.orm.driver.database_config import DatabaseConfig

        parsed = urlparse(url)

        # Extraire le driver et le dialecte (ex: mysql+pymysql -> mysql)
        driver = parsed.scheme.split("+")[0]

        # Gestion des ports par défaut
        default_ports = {"mysql": 3306, "postgresql": 5432, "sqlite": None}

        # Gestion spéciale pour SQLite
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
            charset="utf8mb4",  # Par défaut pour MySQL
        )
