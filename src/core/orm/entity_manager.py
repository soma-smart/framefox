# from typing import Annotated
# import logging
# from injectable import injectable, autowired, Autowired
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, Session
# from src.core.config.settings import Settings


# @injectable
# class EntityManager:
#     """
#     EntityManager is responsible for managing the database sessions and engine.

#     Attributes:
#         engine (Engine): SQLAlchemy engine instance created with the provided database URI.
#         SessionLocal (sessionmaker): SQLAlchemy session factory configured with the provided settings.

#     Methods:
#         __init__(settings: Autowired(Settings)):
#             Initializes the EntityManager with the given settings.

#         get_session() -> Session:
#             Creates and returns a new SQLAlchemy session.
#     """

#     @autowired
#     def __init__(self, settings: Annotated[Settings, Autowired]):

#         self.engine = create_engine(settings.database_url, echo=settings.database_echo)
#         self.SessionLocal = sessionmaker(
#             autocommit=settings.orm_config.get("autocommit", False),
#             autoflush=settings.orm_config.get("autoflush", False),
#             bind=self.engine,
#         )
#         self.logger = logging.getLogger(__name__)

#     def get_session(self) -> Session:
#         return self.SessionLocal()


from typing import Annotated
import logging
from injectable import injectable, autowired, Autowired
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker
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
    def __init__(self, settings: Autowired(Settings)):
        self.engine = create_engine(settings.database_url)
        # self.SessionLocal = Session(self.engine)
        # sessionmaker(class_=Session)
        self.SessionLocal = sessionmaker(
            autocommit=settings.orm_config.get("autocommit", False),
            autoflush=settings.orm_config.get("autoflush", False),
            bind=self.engine,
            class_=Session
        )
        self.logger = logging.getLogger(__name__)

    def get_session(self) -> Session:
        return self.SessionLocal()
