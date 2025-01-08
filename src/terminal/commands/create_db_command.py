from typing import Annotated
from injectable import autowired, Autowired
from sqlmodel import create_engine
import pymysql
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from urllib.parse import urlparse
from src.terminal.commands.abstract_command import AbstractCommand
from src.core.config.settings import Settings


class CreateDbCommand(AbstractCommand):
    @autowired
    def __init__(self, settings: Annotated[Settings, Autowired]):
        super().__init__('create_db')
        self.db_types = [
            "sqlite",
            "postgresql",
            "mysql"
        ]
        self.database_url = settings.database_url

    def execute(self):
        """
        Analyser le DATABASE_URL pour déduire le type de db à créer selon les choix :
            SQLite
            PostgreSQL
            MySQL
        """
        for db_type in self.db_types:
            if db_type in self.database_url:
                if db_type == "sqlite":
                    CreateDbCommand.create_db_sqlite(self.database_url)
                elif db_type == "postgresql":
                    user, password, host, port, database = CreateDbCommand.parse_database_url(
                        self.database_url)
                    CreateDbCommand.create_db_postgresql(
                        user, password, host, port, database)
                elif db_type == "mysql":
                    user, password, host, port, database = CreateDbCommand.parse_database_url(
                        self.database_url)
                    CreateDbCommand.create_db_mysql(
                        user, password, host, port, database)
                break

    @staticmethod
    def create_db_sqlite(database_url: str):
        create_engine(database_url, echo=True)
        print("Base de données créée avec succès.")

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
            print(f"La base de données '{database}' existe déjà.")
        else:
            cursor.execute(f"CREATE DATABASE {database};")
            print(f"Base de données '{database}' créée avec succès.")
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
            print(f"La base de données '{database}' existe déjà.")
        else:
            cursor.execute(f"CREATE DATABASE {database};")
            print(f"Base de données '{database}' créée avec succès.")
        cursor.close()
        connection.close()

    @staticmethod
    def parse_database_url(database_url: str):
        # Analyse l'URL
        parsed_url = urlparse(database_url)

        # Récupère les composants nécessaires
        user = parsed_url.username
        password = parsed_url.password
        host = parsed_url.hostname
        port = parsed_url.port
        database = parsed_url.path[1:]

        return user, password, host, port, database
