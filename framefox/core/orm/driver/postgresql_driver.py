from sqlalchemy import text

from framefox.core.orm.driver.database_config import DatabaseConfig
from framefox.core.orm.driver.database_driver import DatabaseDriver


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
                dbname="postgres",  # Base de données par défaut pour la connexion initiale
            )
        except Exception as e:
            print(f"Erreur de connexion PostgreSQL: {str(e)}")
            raise

    def create_database(self, name: str) -> bool:
        try:
            with self.connect() as connection:
                connection.autocommit = True  # Nécessaire pour CREATE DATABASE
                with connection.cursor() as cursor:
                    # Vérifier si la base existe avant de la créer
                    if not self.database_exists(name):
                        cursor.execute(f'CREATE DATABASE "{name}"')
            return True
        except Exception as e:
            print(f"Erreur lors de la création de la base de données: {str(e)}")
            return False

    def create_alembic_version_table(self, engine):
        """Crée la table alembic_version si elle n'existe pas pour PostgreSQL"""
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
                print("Table alembic_version créée avec succès (PostgreSQL)")
                return True
        except Exception as e:
            print(f"Erreur lors de la création de la table alembic_version: {str(e)}")
            return False

    def database_exists(self, name: str) -> bool:
        try:
            with self.connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT 1 FROM pg_database WHERE datname = %s", (name,)
                    )
                    return cursor.fetchone() is not None
        except Exception as e:
            print(f"Erreur lors de la vérification de la base de données: {str(e)}")
            return False

    def drop_database(self, name: str) -> bool:
        try:
            with self.connect() as connection:
                connection.autocommit = True  # Nécessaire pour DROP DATABASE
                with connection.cursor() as cursor:
                    cursor.execute(f'DROP DATABASE IF EXISTS "{name}"')
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression de la base de données: {str(e)}")
            return False
