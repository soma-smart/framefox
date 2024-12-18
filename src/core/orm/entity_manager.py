from typing import Annotated
import logging
from injectable import injectable, autowired, Autowired
from sqlmodel import create_engine, Session
from src.core.config.settings import Settings

# from sqlalchemy.orm import sessionmaker


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
        # self.SessionLocal = sessionmaker(
        #     autocommit=settings.orm_config.get("autocommit", False),
        #     autoflush=settings.orm_config.get("autoflush", False),
        #     bind=self.engine,
        #     class_=Session
        # )
        self.logger = logging.getLogger(__name__)

    def get_session(self) -> Session:
        # return self.SessionLocal()
        return Session(self.engine)
