from sqlalchemy.sql import text

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
            print(f"SQLite connection error: {str(e)}")
            raise

    def create_database(self, name: str) -> bool:
        try:
            with self.connect() as connection:
                connection.execute("SELECT 1")
            return True
        except Exception as e:
            print(f"Error creating database: {str(e)}")
            return False

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
                print("alembic_version table created successfully (SQLite)")
                return True
        except Exception as e:
            print(f"Error creating alembic_version table: {str(e)}")
            return False

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
            print(f"Error dropping database: {str(e)}")
            return False
