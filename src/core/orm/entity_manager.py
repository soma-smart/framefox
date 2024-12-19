from typing import Annotated
import logging
from injectable import injectable, autowired, Autowired
from sqlmodel import create_engine, Session
from src.core.config.settings import Settings


@injectable
class EntityManager:
    """
    EntityManager is responsible for managing the database sessions and engine.

    Attributes:
        engine (Engine): SQLModel engine instance created with the provided database URI.
        SessionLocal (sessionmaker): SQLModel session factory configured with the provided settings.

    Methods:
        __init__(settings: Autowired(Settings)):
            Initializes the EntityManager with the given settings.

        get_session() -> Session:
            Creates and returns a new SQLModel session.
    """

    @autowired
    def __init__(self, settings: Annotated[Settings, Autowired]):
        self.engine = create_engine(settings.database_url, echo=True)
        self.logger = logging.getLogger(__name__)

    def get_session(self) -> Session:
        """
        Returns a new SQLModel session.

        Returns:
            Session: The newly created session.
        """
        return Session(self.engine)

    def commit(self, session: Session) -> None:
        """
        Commits the changes made in the session.

        Args:
            session (Session): The session to commit.
        """
        session.commit()

    def persist(self, session: Session, entity) -> None:
        """
        Persists an entity in the session.

        Args:
            session (Session): The session to persist the entity in.
            entity: The entity to persist.
        """
        session.add(entity)
        session.flush()

    def delete(self, session: Session, entity) -> None:
        """
        Deletes an entity from the session.

        Args:
            session (Session): The session to delete the entity from.
            entity: The entity to delete.
        """
        session.delete(entity)
        session.flush()

    def refresh(self, session: Session, entity) -> None:
        """
        Refreshes the state of an entity in the session.

        Args:
            session (Session): The session to refresh the entity in.
            entity: The entity to refresh.
        """
        session.refresh(entity)
        session.flush()

    def exec_statement(self, statement) -> None:
        """
        Executes a SQL statement.

        Args:
            statement: The SQL statement to execute.

        Returns:
            None
        """
        with self.get_session() as session:
            return session.exec(statement).all()

    def get_entity(self, entity, id) -> None:
        """
        Retrieves an entity from the session by its ID.

        Args:
            entity: The entity class.
            id: The ID of the entity.

        Returns:
            None
        """
        with self.get_session() as session:
            return session.get(entity, id)
