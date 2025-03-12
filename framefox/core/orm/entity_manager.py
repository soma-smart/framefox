import logging
from typing import Any
from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine
from framefox.core.config.settings import Settings
from framefox.core.di.service_container import ServiceContainer
from framefox.core.orm.connection_manager import ConnectionManager
from framefox.core.orm.abstract_repository import AbstractRepository
"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël & BOUMAZA Rayen
Github: https://github.com/Vasulvius & https://github.com/RayenBou
"""


class EntityManager:
    """
    The EntityManager class provides methods for managing entities in a session.

    Attributes:
        engine: The database engine.
        logger: The logger object.
        session: The session object.
    """

    _instance = None

    @classmethod
    def get_instance(cls) -> "EntityManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.settings = ServiceContainer().get(Settings)
        self.connection_manager = ConnectionManager.get_instance()
        self.logger = logging.getLogger(__name__)
        db_url = self._get_database_url_string()
        self.engine = create_engine(db_url, echo=self.settings.database_echo)
        self.session = Session(self.engine)

    def _get_database_url_string(self) -> str:
        db_config = self.settings.database_url

        if isinstance(db_config, str):
            return db_config

        if db_config.driver == "sqlite":
            return f"sqlite:///{db_config.database}"

        dialect = "mysql+pymysql" if db_config.driver == "mysql" else db_config.driver

        username = str(db_config.username) if db_config.username else ""
        password = str(db_config.password) if db_config.password else ""
        host = str(db_config.host) if db_config.host else "localhost"
        port = str(db_config.port) if db_config.port else "3306"
        database = str(db_config.database) if db_config.database else ""

        return f"{dialect}://{username}:{password}@{host}:{port}/{database}"

    def get_engine(self) -> Engine:
        """Returns the SQLAlchemy engine instance"""
        return self.engine

    def external_connection(self, database_url: str) -> Session:
        """
        Creates a new session with a different database URL.

        Args:
            database_url (str): The database URL to connect to.

        Returns:
            Session: A new SQLModel session.
        """
        new_engine = create_engine(
            database_url, echo=self.settings.database_echo)
        new_session = Session(new_engine)
        return new_session

    def commit(self) -> None:
        """Commits the changes made in the session."""
        self.session.commit()

    def rollback(self) -> None:
        """Rolls back the uncommitted changes in the session."""
        self.session.rollback()

    def persist(self, entity) -> None:
        """
        Persists an entity in the session.

        Args:
            entity: The entity to persist.
        """
        db_entity = self.find_existing_entity(entity)
        if db_entity:
            self.session.merge(entity)
        else:
            self.session.add(entity)

    def delete(self, entity) -> None:
        """
        Deletes an entity from the session.

        Args:
            entity: The entity to delete.
        """
        if self.session.object_session(entity) is not self.session:
            entity = self.session.merge(entity)
        self.session.delete(entity)

    def refresh(self, entity) -> None:
        """
        Refreshes the state of an entity in the session.

        Args:
            entity: The entity to refresh.
        """
        self.session.refresh(entity)

    def exec_statement(self, statement) -> list:
        """
        Executes an SQL statement.

        Args:
            statement: The SQL statement to execute.

        Returns:
            list: List of results.
        """
        return self.session.exec(statement).all()

    def find(self, entity_class, primary_keys) -> Any:
        """
        Retrieves an entity from the session by its primary key.

        Args:
            entity_class: The entity class.
            primary_keys (dict): The primary key values of the entity.

        Returns:
            The found entity or None.
        """
        return self.session.get(entity_class, primary_keys)

    def find_existing_entity(self, entity) -> Any:
        """
        Finds an existing entity in the database based on its primary keys.

        Args:
            entity: The entity object to search for.

        Returns:
            The found entity object, or None if not found.
        """
        primary_keys = entity.get_primary_keys()
        keys = {key: getattr(entity, key) for key in primary_keys}
        return self.find(entity.__class__, keys)

    def create_all_tables(self) -> None:
        """
        Creates all tables defined in SQLModel.metadata.
        Useful for database initialization.
        """
        from sqlmodel import SQLModel

        SQLModel.metadata.create_all(self.engine)

    def drop_all_tables(self) -> None:
        """
        Drops all tables defined in SQLModel.metadata.
        Warning: this operation is destructive!
        """
        from sqlmodel import SQLModel

        SQLModel.metadata.drop_all(self.engine)

    def get_repository(self, entity_class):
        """
        Obtient un repository pour une classe d'entité spécifique.

        Args:
            entity_class: La classe de l'entité.

        Returns:
            AbstractRepository: Une instance de repository pour l'entité spécifiée.
        """
        container = ServiceContainer()
        repositories = container.get_by_tag_prefix("repository.")

        for repo in repositories:
            if getattr(repo, "model", None) == entity_class:
                return repo
            else:
                return None
