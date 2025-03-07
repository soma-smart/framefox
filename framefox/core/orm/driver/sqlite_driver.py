from sqlalchemy.sql import text

from framefox.core.orm.driver.database_config import DatabaseConfig
from framefox.core.orm.driver.database_driver import DatabaseDriver


class SQLiteDriver(DatabaseDriver):
    def __init__(self, config: DatabaseConfig):
        self.config = config

    def connect(self):
        import sqlite3

        try:
            # Pour SQLite, database est le chemin du fichier
            return sqlite3.connect(self.config.database)
        except Exception as e:
            print(f"Erreur de connexion SQLite: {str(e)}")
            raise

    def create_database(self, name: str) -> bool:
        try:
            # Pour SQLite, la création de la base se fait à la connexion
            # On crée simplement le fichier s'il n'existe pas
            with self.connect() as connection:
                connection.execute("SELECT 1")  # Simple test de connexion
            return True
        except Exception as e:
            print(f"Erreur lors de la création de la base de données: {str(e)}")
            return False

    def create_alembic_version_table(self, engine):
        """Crée la table alembic_version si elle n'existe pas pour SQLite"""
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
                print("Table alembic_version créée avec succès (SQLite)")
                return True
        except Exception as e:
            print(f"Erreur lors de la création de la table alembic_version: {str(e)}")
            return False

    def database_exists(self, name: str) -> bool:
        import os

        # Pour SQLite, on vérifie si le fichier existe
        return os.path.exists(self.config.database)

    def drop_database(self, name: str) -> bool:
        import os

        try:
            if self.database_exists(name):
                os.remove(self.config.database)
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression de la base de données: {str(e)}")
            return False
