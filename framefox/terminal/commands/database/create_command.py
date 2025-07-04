from sqlalchemy import text

from framefox.core.config.settings import Settings
from framefox.terminal.commands.database.abstract_database_command import (
    AbstractDatabaseCommand,
)

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class CreateCommand(AbstractDatabaseCommand):
    def __init__(self):
        super().__init__()
        settings = Settings()
        self.db_types = ["sqlite", "postgresql", "mysql"]
        self.database_url = settings.database_url

    def execute(self):
        """
        Create the empty database if it doesn't exist.
        """
        try:
            database = self.connection_manager.config.database

            if self.driver.database_exists(database):
                self.printer.print_msg(f"The database '{database}' already exists", theme="warning")
                return

            self.driver.create_database(database)
            self.printer.print_msg(f"Database '{database}' created successfully", theme="success")

        except Exception as e:
            self.printer.print_msg(
                f"Error while creating the database: {str(e)}",
                theme="error",
            )

    def create_alembic_version_table(self, engine):
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
