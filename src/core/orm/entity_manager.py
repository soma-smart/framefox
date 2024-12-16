from injectable import injectable, autowired, Autowired
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.core.config.settings import Settings


@injectable
class EntityManager:
    @autowired
    def __init__(self, settings: Autowired(Settings)):
        self.engine = create_engine(
            settings.database_uri,
            echo=settings.database_echo
        )
        self.SessionLocal = sessionmaker(
            autocommit=settings.orm_config.get('autocommit', False),
            autoflush=settings.orm_config.get('autoflush', False),
            bind=self.engine
        )

    def get_session(self) -> Session:
        return self.SessionLocal()
