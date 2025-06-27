from sqlalchemy import text

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


class PostgreSQLDriver(DatabaseDriver):
    def __init__(self, config: DatabaseConfig):
        self.config = config

    def connect(self):
        import psycopg2

        try:
            password = str(self.config.password) if self.config.password else ""

            return psycopg2.connect(
                host=str(self.config.host),
                port=int(self.config.port),
                user=str(self.config.username),
                password=password,
                dbname="postgres",
            )
        except Exception as e:
            raise DatabaseConnectionError(f"PostgreSQL connection failed: {str(e)}", e)

    def create_database(self, name: str) -> bool:
        try:
            import psycopg2

            conn = psycopg2.connect(
                host=str(self.config.host),
                port=int(self.config.port),
                user=str(self.config.username),
                password=str(self.config.password) if self.config.password else "",
                dbname="postgres",
            )
            conn.autocommit = True

            with conn.cursor() as cursor:
                if not self.database_exists(name):
                    cursor.execute(f'CREATE DATABASE "{name}"')

            conn.close()
            return True
        except Exception as e:
            raise DatabaseCreationError(name, e)

    def create_alembic_version_table(self, engine):
        """Creates the alembic_version table if it does not exist for PostgreSQL"""
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
            raise DatabaseDriverError("PostgreSQL", "create alembic_version table", e)

    def database_exists(self, name: str) -> bool:
        try:
            with self.connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (name,))
                    return cursor.fetchone() is not None
        except Exception as e:
            raise DatabaseDriverError("PostgreSQL", "check database existence", e)

    def drop_database(self, name: str) -> bool:
        try:
            import psycopg2

            conn = psycopg2.connect(
                host=str(self.config.host),
                port=int(self.config.port),
                user=str(self.config.username),
                password=str(self.config.password) if self.config.password else "",
                dbname="postgres",
            )
            conn.autocommit = True

            with conn.cursor() as cursor:
                cursor.execute(f'DROP DATABASE IF EXISTS "{name}"')

            conn.close()
            return True
        except Exception as e:
            raise DatabaseDropError(name, e)
