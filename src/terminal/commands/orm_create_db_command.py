from typing import Annotated
from injectable import autowired, Autowired
from sqlmodel import create_engine, SQLModel
import pymysql
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from src.terminal.common.database_url_parser import DatabaseUrlParser
from src.terminal.commands.abstract_command import AbstractCommand
from src.core.config.settings import Settings


class OrmCreateDbCommand(AbstractCommand):
    @autowired
    def __init__(self, settings: Annotated[Settings, Autowired]):
        super().__init__('orm_create_db')
        self.db_types = [
            "sqlite",
            "postgresql",
            "mysql"
        ]
        self.database_url = settings.database_url

    def execute(self):
        """
        Analyze the DATABASE_URL to determine the type of database to create based on the choices:
            SQLite
            PostgreSQL
            MySQL
        """
        for db_type in self.db_types:
            if db_type in self.database_url:
                if db_type == "sqlite":
                    OrmCreateDbCommand.create_db_sqlite(self.database_url)
                elif db_type == "postgresql":
                    _, user, password, host, port, database = DatabaseUrlParser.parse_database_url(
                        self.database_url)
                    OrmCreateDbCommand.create_db_postgresql(
                        user, password, host, port, database)
                elif db_type == "mysql":
                    _, user, password, host, port, database = DatabaseUrlParser.parse_database_url(
                        self.database_url)
                    OrmCreateDbCommand.create_db_mysql(
                        user, password, host, port, database)
                break

    @staticmethod
    def create_db_sqlite(database_url: str):
        engine = create_engine(database_url, echo=True)
        SQLModel.metadata.create_all(engine)
        print("Database created successfully.")

    @staticmethod
    def create_db_postgresql(user: str, password: str, host: str, port: int, database: str):
        connection = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        cursor.execute(
            f"SELECT 1 FROM pg_database WHERE datname = '{database}';")
        if cursor.fetchone():
            print(f"The database '{database}' already exists.")
        else:
            cursor.execute(f"CREATE DATABASE {database};")
            print(f"Database '{database}' created successfully.")
        cursor.close()
        connection.close()

    @staticmethod
    def create_db_mysql(user: str, password: str, host: str, port: int, database: str):
        connection = pymysql.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        cursor = connection.cursor()
        cursor.execute(f"SHOW DATABASES LIKE '{database}';")
        result = cursor.fetchone()
        if result:
            print(f"The database '{database}' already exists.")
        else:
            cursor.execute(f"CREATE DATABASE {database};")
            print(f"Database '{database}' created successfully.")
        cursor.close()
        connection.close()
