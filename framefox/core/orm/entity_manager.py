import logging

from sqlmodel import Session, create_engine

from framefox.core.config.settings import Settings
from framefox.core.di.service_container import ServiceContainer

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class EntityManager:
    """
    The EntityManager class provides methods for managing entities in a session.

    Args:
        settings (Annotated[Settings, Autowired]): The settings object containing the database URL.

    Attributes:
        engine: The database engine.
        logger: The logger object.
        session: The session object.

    """

    def __init__(self):
        self._instance_id = id(self)
        self.settings = ServiceContainer().get(Settings)
        self.engine = create_engine(self.settings.database_url, echo=True)
        self.logger = logging.getLogger(__name__)
        self.session = Session(self.engine)

    def get_instance_id(self):
        return self._instance_id

    def external_connection(self, database_url: str) -> Session:
        """
        Creates a new session with a different database URL.

        Args:
            database_url (str): The database URL to connect to.

        Returns:
            Session: A new SQLModel session.
        """
        new_engine = create_engine(database_url, echo=True)
        new_session = Session(new_engine)
        return new_session

    def commit(self) -> None:
        """
        Commits the changes made in the session.
        """
        self.session.commit()

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

    def exec_statement(self, statement) -> None:
        """
        Executes a SQL statement.

        Args:
            statement: The SQL statement to execute.
        """
        return self.session.exec(statement).all()

    def find(self, entity, primary_keys) -> None:
        """
        Retrieves an entity from the session by its ID.

        Args:
            entity: The entity class.
            primary_keys (dict): The primary keys with values of the entity.
        """
        return self.session.get(entity, primary_keys)

    def find_existing_entity(self, entity):
        """
        Find an existing entity in the database based on its primary keys.

        Args:
            entity: The entity object to search for.

        Returns:
            The found entity object, or None if not found.
        """
        primary_keys = entity.get_primary_keys()
        keys = {key: getattr(entity, key) for key in primary_keys}
        return self.find(entity.__class__, keys)
