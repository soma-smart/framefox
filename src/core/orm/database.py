from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config.settings import Settings


class Database:
    def __init__(self, setting):
        self.settings = setting
        self.engine = create_engine(
            self.settings.database_uri,
            echo=self.settings.database_echo
        )
        self.SessionLocal = sessionmaker(
            autocommit=self.settings.orm_config.get('autocommit', False),
            autoflush=self.settings.orm_config.get('autoflush', False),
            bind=self.engine
        )

    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
