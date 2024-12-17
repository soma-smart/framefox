from typing import Annotated
from injectable import injectable, autowired, Autowired
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.core.config.settings import Settings


@injectable
class EntityManager:
    """
    EntityManager is responsible for managing the database sessions and engine.

    Attributes:
        engine (Engine): SQLAlchemy engine instance created with the provided database URI.
        SessionLocal (sessionmaker): SQLAlchemy session factory configured with the provided settings.

    Methods:
        __init__(settings: Autowired(Settings)):
            Initializes the EntityManager with the given settings.

        get_session() -> Session:
            Creates and returns a new SQLAlchemy session.
    """

    @autowired
    def __init__(self, settings: Annotated[Settings, Autowired]):
        self.engine = create_engine(settings.database_url, echo=settings.database_echo)
        self.SessionLocal = sessionmaker(
            autocommit=settings.orm_config.get("autocommit", False),
            autoflush=settings.orm_config.get("autoflush", False),
            bind=self.engine,
        )

    def get_session(self) -> Session:
        return self.SessionLocal()
