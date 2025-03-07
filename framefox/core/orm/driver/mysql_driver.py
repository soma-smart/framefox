from sqlalchemy.sql import text

from framefox.core.orm.driver.database_config import DatabaseConfig
from framefox.core.orm.driver.database_driver import DatabaseDriver


class MySQLDriver(DatabaseDriver):
    def __init__(self, config: DatabaseConfig):
        self.config = config

    def connect(self):
        import pymysql

        try:

            password = str(self.config.password) if self.config.password else ""

            return pymysql.connect(
                host=str(self.config.host),
                port=int(self.config.port),
                user=str(self.config.username),
                password=password,
                charset=str(self.config.charset),
            )
        except Exception as e:
            print(f"Erreur de connexion MySQL: {str(e)}")
            raise

    def create_database(self, name: str) -> bool:
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{name}` CHARACTER SET {self.config.charset}"
                )
            connection.commit()
        return True

    def create_alembic_version_table(self, engine):
        """Crée la table alembic_version si elle n'existe pas pour MySQL"""
        try:
            with engine.connect() as connection:
                connection.execute(
                    text(
                        """
                        CREATE TABLE IF NOT EXISTS alembic_version (
                            version_num VARCHAR(32) NOT NULL PRIMARY KEY
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                        """
                    )
                )
                connection.commit()
                print("Table alembic_version créée avec succès (MySQL)")
                return True
        except Exception as e:
            print(f"Erreur lors de la création de la table alembic_version: {str(e)}")
            return False

    def database_exists(self, name: str) -> bool:
        """Vérifie si la base de données existe"""
        try:
            with self.connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(f"SHOW DATABASES LIKE '{name}'")
                    return cursor.fetchone() is not None
        except Exception as e:
            print(f"Erreur lors de la vérification de la base de données: {str(e)}")
            return False

    def drop_database(self, name: str) -> bool:
        """Supprime la base de données"""
        try:
            with self.connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(f"DROP DATABASE IF EXISTS `{name}`")
                connection.commit()
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression de la base de données: {str(e)}")
            return False
