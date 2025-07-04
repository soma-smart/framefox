from abc import ABC

from framefox.core.orm.connection_manager import ConnectionManager
from framefox.core.orm.driver.database_config import DatabaseConfig
from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.database_url_parser import DatabaseUrlParser

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class AbstractDatabaseCommand(AbstractCommand, ABC):
    def __init__(self, name: str = None):
        super().__init__(name)
        self._connection_manager = None

    @property
    def connection_manager(self):
        """Lazy loading du connection manager pour éviter les erreurs à l'instanciation"""
        if self._connection_manager is None:
            self._connection_manager = ConnectionManager.get_instance()
        return self._connection_manager

    @property
    def driver(self):
        return self.connection_manager.driver

    def _create_connection_manager(self) -> ConnectionManager:
        parser = DatabaseUrlParser()
        scheme, user, password, host, port, database = parser.parse(self.settings.database_url)

        config = DatabaseConfig(
            driver=scheme.split("+")[0],
            host=host,
            port=port or self._get_default_port(scheme),
            username=user,
            password=password,
            database=database,
        )

        return ConnectionManager(config)

    def _get_default_port(self, driver: str) -> int:
        return {"mysql": 3306, "postgresql": 5432, "sqlite": 0}.get(driver, 0)
