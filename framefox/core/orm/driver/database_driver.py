from abc import ABC, abstractmethod
from typing import Any

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


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
        """Creates the alembic_version table if it does not exist"""
        pass
