from typing import Dict

from sqlalchemy.engine import Engine
from sqlmodel import create_engine

from framefox.core.config.settings import Settings
from framefox.core.request.request_stack import RequestStack


class EntityManagerRegistry:
    """Manages EntityManager instances and their configurations"""

    _instance = None
    _engines: Dict[str, Engine] = {}

    @classmethod
    def get_instance(cls) -> "EntityManagerRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self.settings = Settings()
        self._initialized = True

    def get_engine(self, connection_name: str = "default") -> Engine:
        """Retrieves or creates a configured database engine"""
        if connection_name not in self._engines:
            db_url = self._get_database_url_string(connection_name)
            db_config = self.settings.config.get("database", {})

            self._engines[connection_name] = create_engine(
                db_url,
                echo=self.settings.database_echo,
                pool_size=db_config.get("pool_size", 20),
                max_overflow=db_config.get("max_overflow", 10),
                pool_timeout=db_config.get("pool_timeout", 30),
                pool_recycle=db_config.get("pool_recycle", 1800),
                pool_pre_ping=db_config.get("pool_pre_ping", True),
            )
        return self._engines[connection_name]

    def _get_database_url_string(self, connection_name: str = "default") -> str:
        """Retrieves the database URL according to the configuration"""
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

    @classmethod
    def get_entity_manager_for_request(cls, request=None):
        """Gets the EntityManager for the current request or creates a new one"""
        from framefox.core.orm.entity_manager import EntityManager

        if request is None:
            request = RequestStack.get_request()

        if request and hasattr(request.state, "entity_manager"):
            return request.state.entity_manager

        em = EntityManager()

        if request:
            request.state.entity_manager = em

        return em

    @classmethod
    def get_entity_manager_for_worker(cls):
        """Crée un EntityManager persistant pour les workers (contexte non-HTTP)"""
        from framefox.core.orm.entity_manager import EntityManager

        return EntityManager()
