from sqlalchemy.sql import text

from framefox.core.debug.exception.database_exception import (
    DatabaseConnectionError,
    DatabaseCreationError,
    DatabaseDriverError,
    DatabaseDropError,
)
from framefox.core.orm.driver.database_config import DatabaseConfig
from framefox.core.orm.driver.database_driver import DatabaseDriver

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class SQLiteDriver(DatabaseDriver):
    def __init__(self, config: DatabaseConfig):
        self.config = config

    def connect(self):
        import sqlite3

        try:
            return sqlite3.connect(self.config.database)
        except Exception as e:
            raise DatabaseConnectionError(f"SQLite connection failed: {str(e)}", e)

    def create_database(self, name: str) -> bool:
        try:
            with self.connect() as connection:
                connection.execute("SELECT 1")
            return True
        except Exception as e:
            raise DatabaseCreationError(name, e)

    def create_alembic_version_table(self, engine):
        """Creates the alembic_version table if it does not exist for SQLite"""
        try:
            with engine.connect() as connection:
                connection.execute(
                    text(
                        """
                        CREATE TABLE IF NOT EXISTS alembic_version (
                            version_num VARCHAR(32) NOT NULL PRIMARY KEY
                        );
                        """
                    )
                )
                connection.commit()
                return True
        except Exception as e:
            raise DatabaseDriverError("SQLite", "create alembic_version table", e)

    def database_exists(self, name: str) -> bool:
        import os

        return os.path.exists(self.config.database)

    def drop_database(self, name: str) -> bool:
        import os

        try:
            if self.database_exists(name):
                os.remove(self.config.database)
            return True
        except Exception as e:
            raise DatabaseDropError(name, e)
