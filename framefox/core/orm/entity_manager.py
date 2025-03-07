import logging
from typing import Any, Dict, Optional

from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine

from framefox.core.config.settings import Settings
from framefox.core.di.service_container import ServiceContainer
from framefox.core.orm.connection_manager import ConnectionManager

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
        self._instance_id = id(self)
        self.settings = ServiceContainer().get(Settings)
        self.connection_manager = ConnectionManager.get_instance()
        self.logger = logging.getLogger(__name__)

        # Création de l'engine SQLAlchemy à partir de l'URL formatée
        db_url = self._get_database_url_string()
        self.engine = create_engine(db_url, echo=self.settings.database_echo)
        self.session = Session(self.engine)

    def get_instance_id(self) -> int:
        """Retourne l'ID unique de cette instance"""
        return self._instance_id

    def _get_database_url_string(self) -> str:
        """Convertit la configuration de base de données en URL utilisable par SQLAlchemy"""
        db_config = self.settings.database_url

        # Si c'est déjà une chaîne, la retourner directement
        if isinstance(db_config, str):
            return db_config

        # Sinon, construire l'URL à partir de l'objet DatabaseConfig
        if db_config.driver == "sqlite":
            return f"sqlite:///{db_config.database}"

        dialect = "mysql+pymysql" if db_config.driver == "mysql" else db_config.driver

        # Mettre des valeurs par défaut pour les éléments manquants
        username = str(db_config.username) if db_config.username else ""
        password = str(db_config.password) if db_config.password else ""
        host = str(db_config.host) if db_config.host else "localhost"
        port = str(db_config.port) if db_config.port else "3306"
        database = str(db_config.database) if db_config.database else ""

        return f"{dialect}://{username}:{password}@{host}:{port}/{database}"

    def get_engine(self) -> Engine:
        """Retourne l'instance de l'engine SQLAlchemy"""
        return self.engine

    def external_connection(self, database_url: str) -> Session:
        """
        Crée une nouvelle session avec une URL de base de données différente.

        Args:
            database_url (str): L'URL de la base de données à laquelle se connecter.

        Returns:
            Session: Une nouvelle session SQLModel.
        """
        new_engine = create_engine(database_url, echo=self.settings.database_echo)
        new_session = Session(new_engine)
        return new_session

    def commit(self) -> None:
        """Valide les modifications effectuées dans la session."""
        self.session.commit()

    def rollback(self) -> None:
        """Annule les modifications non validées dans la session."""
        self.session.rollback()

    def persist(self, entity) -> None:
        """
        Persiste une entité dans la session.

        Args:
            entity: L'entité à persister.
        """
        db_entity = self.find_existing_entity(entity)
        if db_entity:
            self.session.merge(entity)
        else:
            self.session.add(entity)

    def delete(self, entity) -> None:
        """
        Supprime une entité de la session.

        Args:
            entity: L'entité à supprimer.
        """
        if self.session.object_session(entity) is not self.session:
            entity = self.session.merge(entity)
        self.session.delete(entity)

    def refresh(self, entity) -> None:
        """
        Rafraîchit l'état d'une entité dans la session.

        Args:
            entity: L'entité à rafraîchir.
        """
        self.session.refresh(entity)

    def exec_statement(self, statement) -> list:
        """
        Exécute une instruction SQL.

        Args:
            statement: L'instruction SQL à exécuter.

        Returns:
            list: Liste des résultats.
        """
        return self.session.exec(statement).all()

    def find(self, entity_class, primary_keys) -> Any:
        """
        Récupère une entité de la session par sa clé primaire.

        Args:
            entity_class: La classe de l'entité.
            primary_keys (dict): Les valeurs des clés primaires de l'entité.

        Returns:
            L'entité trouvée ou None.
        """
        return self.session.get(entity_class, primary_keys)

    def find_existing_entity(self, entity) -> Any:
        """
        Trouve une entité existante dans la base de données en fonction de ses clés primaires.

        Args:
            entity: L'objet entité à rechercher.

        Returns:
            L'objet entité trouvé, ou None si non trouvé.
        """
        primary_keys = entity.get_primary_keys()
        keys = {key: getattr(entity, key) for key in primary_keys}
        return self.find(entity.__class__, keys)

    def create_all_tables(self) -> None:
        """
        Crée toutes les tables définies dans SQLModel.metadata.
        Utile pour l'initialisation de la base de données.
        """
        from sqlmodel import SQLModel

        SQLModel.metadata.create_all(self.engine)

    def drop_all_tables(self) -> None:
        """
        Supprime toutes les tables définies dans SQLModel.metadata.
        Attention: cette opération est destructive!
        """
        from sqlmodel import SQLModel

        SQLModel.metadata.drop_all(self.engine)
