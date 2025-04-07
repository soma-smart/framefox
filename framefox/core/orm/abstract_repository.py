from abc import ABC
from typing import List, Optional, Type, TypeVar

from sqlmodel import SQLModel, asc, desc, select

from framefox.core.orm.entity_manager_registry import EntityManagerRegistry
from framefox.core.orm.query_builder import QueryBuilder

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""

T = TypeVar("T", bound=SQLModel)


class AbstractRepository(ABC):
    """
    AbstractRepository provides the following methods:

    - find(id): Retrieve an entity by its ID.
    - find_all(): Retrieve all entities.
    - find_by(criteria): Retrieve entities based on specific criteria.
    """

    def __init__(
        self,
        model: Type[T],
    ):
        self.model = model

        self.create_model = self.model.generate_create_model()
        # self.response_model = self.model.generate_models_response()

    @property
    def entity_manager(self):
        return EntityManagerRegistry.get_entity_manager_for_request()

    def find(self, id) -> Optional[T]:
        """
        Retrieve an entity by its ID.

        Args:
            id: The keys of an entity.

        Returns:
            Optional[T]: The retrieved entity, or None if not found.
        """
        return self.entity_manager.find(self.model, id)

    def find_all(self) -> List[T]:
        """
        Retrieve all entities.

        Returns:
            List[T]: A list of all entities.
        """
        statement = select(self.model)
        return self.entity_manager.exec_statement(statement)

    def find_by(self, criteria, order_by=None, limit=None, offset=None) -> List[T]:
        """
        Retrieve entities based on specific criteria.

        Args:
            criteria: The criteria to filter the entities.
            order_by: The field(s) to order the entities by.
            limit: The maximum number of entities to retrieve.
            offset: The number of entities to skip.

        Returns:
            List[T]: A list of entities that match the criteria.
        """
        statement = select(self.model).filter_by(**criteria)
        if order_by:
            for field, direction in order_by.items():
                if direction.lower() == "asc":
                    statement = statement.order_by(asc(getattr(self.model, field)))
                elif direction.lower() == "desc":
                    statement = statement.order_by(desc(getattr(self.model, field)))

        if limit is not None:
            statement = statement.limit(limit)

        if offset is not None:
            statement = statement.offset(offset)
        return self.entity_manager.exec_statement(statement)

    def get_query_builder(self) -> QueryBuilder:
        """
        Retrieve an instance of QueryBuilder for the specific entity of the repository.

        Returns:
            QueryBuilder: An instance configured for the repository's entity.
        """
        return QueryBuilder(entity_manager=self.entity_manager, model=self.model)
