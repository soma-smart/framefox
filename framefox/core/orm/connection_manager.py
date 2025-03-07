from typing import Dict, Type

from framefox.core.config.settings import Settings
from framefox.core.orm.driver.database_config import DatabaseConfig
from framefox.core.orm.driver.database_driver import DatabaseDriver
from framefox.core.orm.driver.mysql_driver import MySQLDriver
from framefox.core.orm.driver.postgresql_driver import PostgreSQLDriver
from framefox.core.orm.driver.sqlite_driver import SQLiteDriver


class ConnectionManager:
    _instance = None
    _drivers: Dict[str, Type[DatabaseDriver]] = {
        "mysql": MySQLDriver,
        "postgresql": PostgreSQLDriver,
        "sqlite": SQLiteDriver,
    }

    @classmethod
    def get_instance(cls) -> "ConnectionManager":
        """Récupère l'instance unique du ConnectionManager"""
        if cls._instance is None:
            settings = Settings()
            cls._instance = cls(settings.database_url)
        return cls._instance

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._driver = self._create_driver()

    def _create_driver(self) -> DatabaseDriver:
        driver_class = self._drivers.get(self.config.driver)
        if not driver_class:
            raise ValueError(f"Unsupported database driver: {self.config.driver}")
        return driver_class(self.config)

    @property
    def driver(self) -> DatabaseDriver:
        return self._driver
