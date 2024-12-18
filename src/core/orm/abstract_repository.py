from abc import ABC
from typing import Annotated, Type, TypeVar, List, Optional
from sqlmodel import SQLModel, Session, select, asc, desc
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

    def get_session(self) -> Session:
        return self.entity_manager.get_session()

    def find(self, id: int) -> Optional[T]:
        with self.get_session() as session:
            return session.get(self.model, id)

    def find_all(self) -> List[T]:
        with self.get_session() as session:
            statement = select(self.model)
            return session.exec(statement).all()

    def find_by(self, criteria, order_by=None, limit=None, offset=None) -> List[T]:
        with self.get_session() as session:
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
            return session.exec(statement).all()

    def add(self, entity: T) -> None:
        with self.get_session() as session:
            session.add(entity)
            session.commit()

    def update(self, entity_id: int, entity: T) -> None:
        with self.get_session() as session:
            db_entity = session.query(self.model).get(entity_id)
            if entity:
                for key, value in entity.dict().items():
                    setattr(db_entity, key, value)
                session.commit()
                session.refresh(db_entity)
                return db_entity
            return None

    def delete(self, entity_id: int) -> None:
        with self.get_session() as session:
            entity = session.query(self.model).get(entity_id)
            if entity:
                session.delete(entity)
                session.commit()
