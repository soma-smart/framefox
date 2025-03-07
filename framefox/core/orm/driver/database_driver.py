from abc import ABC, abstractmethod
from typing import Any


class DatabaseDriver(ABC):
    @abstractmethod
    def connect(self) -> Any:
        pass

    @abstractmethod
    def create_database(self, name: str) -> bool:
        pass

    @abstractmethod
    def drop_database(self, name: str) -> bool:
        pass

    @abstractmethod
    def database_exists(self, name: str) -> bool:
        pass

    @abstractmethod
    def create_alembic_version_table(self, engine):
        """Crée la table alembic_version si elle n'existe pas"""
        pass
