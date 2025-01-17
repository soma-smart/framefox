from sqlmodel import create_engine, SQLModel
import pymysql
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from framefox.terminal.common.database_url_parser import DatabaseUrlParser
from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.core.config.settings import Settings


class OrmCreateDbCommand(AbstractCommand):
    def __init__(self):
        super().__init__("create")
        settings = Settings()
        self.db_types = ["sqlite", "postgresql", "mysql"]
        self.database_url = settings.database_url

    def execute(self):
        """
        Analyze the DATABASE_URL to determine the type of database to create based on the choices:
            SQLite
            PostgreSQL
            MySQL
        """
        for db_type in self.db_types:
            self.printer.print_msg(
                db_type,
                theme="normal",
                linebefore=True,
            )
            self.printer.print_msg(
                self.database_url,
                theme="bold_normal",
            )
            if db_type in self.database_url:
                if db_type == "sqlite":
                    self.create_db_sqlite(self.database_url)
                elif db_type == "postgresql":
                    _, user, password, host, port, database = (
                        DatabaseUrlParser.parse_database_url(self.database_url)
                    )
                    self.create_db_postgresql(
                        user, password, host, port, database
                    )
                elif db_type == "mysql":
                    _, user, password, host, port, database = (
                        DatabaseUrlParser.parse_database_url(self.database_url)
                    )
                    self.create_db_mysql(
                        user, password, host, port, database
                    )
                break

    def create_db_sqlite(self, database_url: str):
        engine = create_engine(database_url, echo=True)
        SQLModel.metadata.create_all(engine)
        self.printer.print_msg(
            "Database created successfully.",
            theme="success",
            linebefore=True,
            newline=True,
        )
        self.command_suggestion()

    def create_db_postgresql(
        self, user: str, password: str, host: str, port: int, database: str
    ):
        connection = psycopg2.connect(
            user=user, password=password, host=host, port=port, database=database
        )
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        cursor.execute(
            f"SELECT 1 FROM pg_database WHERE datname = '{database}';")
        if cursor.fetchone():
            self.printer.print_msg(
                f"The database '{database}' already exists.",
                theme="warning",
                linebefore=True,
                newline=True,
            )
        else:
            cursor.execute(f"CREATE DATABASE {database};")
            self.printer.print_msg(
                f"Database '{database}' created successfully.",
                theme="success",
                linebefore=True,
                newline=True,
            )
        cursor.close()
        connection.close()
        self.command_suggestion()

    def create_db_mysql(self, user: str, password: str, host: str, port: int, database: str):
        connection = pymysql.connect(
            user=user, password=password, host=host, port=port, database=database
        )
        cursor = connection.cursor()
        cursor.execute(f"SHOW DATABASES LIKE '{database}';")
        result = cursor.fetchone()
        if result:
            self.printer.print_msg(
                f"The database '{database}' already exists.",
                theme="warning",
                linebefore=True,
                newline=True,
            )
        else:
            cursor.execute(f"CREATE DATABASE {database};")
            self.printer.print_msg(
                f"Database '{database}' created successfully.",
                theme="success",
                linebefore=True,
                newline=True,
            )
        cursor.close()
        connection.close()
        self.command_suggestion()

    def command_suggestion(self):
        self.printer.print_full_text(
            "Now you can migrate your database by using [bold green]framefox orm database migrate[/bold green]",
            newline=True,
        )
