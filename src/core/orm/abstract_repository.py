from abc import ABC
from typing import Annotated, Type, TypeVar, List, Optional
from sqlmodel import SQLModel, select, asc, desc
from injectable import Autowired, autowired
from src.core.orm.entity_manager import EntityManager

T = TypeVar("T", bound=SQLModel)


class AbstractRepository(ABC):
    """
    AbstractRepository provides the following methods:

    - find(id): Retrieve an entity by its ID.
    - find_all(): Retrieve all entities.
    - find_by(criteria): Retrieve entities based on specific criteria.
    - add(entity): Add a new entity.
    - update(entity): Update an existing entity.
    - delete(entity): Delete an entity.
    """

    @autowired
    def __init__(self, model: Type[T], entity_manager: Annotated[EntityManager, Autowired]):
        self.model = model
        self.entity_manager = entity_manager
        self.create_model = self.model.generate_create_model()
        # self.response_model = self.model.generate_models_response()

    def find(self, id: int) -> Optional[T]:
        """
        Retrieve an entity by its ID.

        Args:
            id (int): The ID of the entity.

        Returns:
            Optional[T]: The retrieved entity, or None if not found.
        """
        return self.entity_manager.get_entity(self.model, id)

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
                if direction.lower() == 'asc':
                    statement = statement.order_by(
                        asc(getattr(self.model, field)))
                elif direction.lower() == 'desc':
                    statement = statement.order_by(
                        desc(getattr(self.model, field)))

        if limit is not None:
            statement = statement.limit(limit)

        if offset is not None:
            statement = statement.offset(offset)
        return self.entity_manager.exec_statement(statement)

    def add(self, entity: T) -> None:
        """
        Add a new entity.

        Args:
            entity (T): The entity to add.
        """
        with self.entity_manager.get_session() as session:
            self.entity_manager.persist(session, entity)
            self.entity_manager.commit(session)

    def update(self, entity_id: int, entity: T) -> None:
        """
        Update an existing entity.

        Args:
            entity_id (int): The ID of the entity to update.
            entity (T): The updated entity.
        """
        with self.entity_manager.get_session() as session:
            db_entity = session.query(self.model).get(entity_id)
            if entity:
                for key, value in entity.dict().items():
                    setattr(db_entity, key, value)
                self.entity_manager.commit(session)
                self.entity_manager.refresh(session, db_entity)
                return db_entity
            return None

    def delete(self, entity_id: int) -> None:
        """
        Delete an entity.

        Args:
            entity_id (int): The ID of the entity to delete.
        """
        with self.entity_manager.get_session() as session:
            entity = session.query(self.model).get(entity_id)
            if entity:
                self.entity_manager.delete(session, entity)
                self.entity_manager.commit(session)
