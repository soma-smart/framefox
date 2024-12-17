from abc import ABC
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from injectable import Autowired, autowired
from src.core.orm.entity_manager import EntityManager


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
    def __init__(self, model, entity_manager: Annotated[EntityManager, Autowired]):
        self.db: Session = entity_manager.get_session()
        self.model = model
        self.create_model = self.model.generate_models_create()
        self.response_model = self.model.generate_models_response()

    def find(self, entity_id: int):
        """
        Find an entity by its ID.

        Args:
            entity_id (int): The ID of the entity to find.

        Returns:
            The entity with the specified ID, or None if not found.
        """
        return self.db.query(self.model).filter(self.model.id == entity_id).first()

    def find_all(self):
        """
        Retrieve all entities from the database.

        Returns:
            List: A list of entities.
        """
        entities = self.db.query(self.model).all()
        return [self.response_model.from_orm(entity) for entity in entities]

    def find_by(self, criteria, order_by=None, limit=None, offset=None):
        """
        Retrieves items from the repository based on the specified criteria.

        Args:
            criteria: A dictionary of criteria to filter the items.
            order_by: A dictionary specifying the order in which to retrieve the items.
            limit: The maximum number of items to retrieve.
            offset: The number of items to skip from the beginning.

        Returns:
            A list of items that match the specified criteria.
        """
        query = self.db.query(self.model).filter_by(**criteria)

        if order_by:
            for key, value in order_by.items():
                if value.lower() == "asc":
                    query = query.order_by(asc(getattr(self.model, key)))
                elif value.lower() == "desc":
                    query = query.order_by(desc(getattr(self.model, key)))

        if limit:
            query = query.limit(limit)

        if offset:
            query = query.offset(offset)

        return query.all()

    def update(self, entity_id: int, entity):
        """
        Update an entity in the database.

        Args:
            entity_id (int): The ID of the entity to update.
            entity: The updated entity object.

        Returns:
            The updated entity object if it exists in the database, otherwise None.
        """
        db_entity = self.db.query(self.model).filter(self.model.id == entity_id).first()
        if db_entity:
            for key, value in entity.dict().items():
                setattr(db_entity, key, value)
            self.db.commit()
            self.db.refresh(db_entity)
            return db_entity
        return None

    def add(self, entity):
        """
        Add a new entity to the repository.

        Args:
            entity: The entity object to be added.

        Returns:
            The added entity object.

        Raises:
            None.
        """
        db_entity = self.model(**entity.dict())
        self.db.add(db_entity)
        self.db.commit()
        self.db.refresh(db_entity)
        return db_entity

    def delete(self, entity_id: int):
        """Delete an entity from the database.

        Args:
            entity_id (int): The ID of the entity to be deleted.

        Returns:
            The deleted entity if it exists, otherwise None.
        """
        db_entity = self.db.query(self.model).filter(self.model.id == entity_id).first()
        if db_entity:
            self.db.delete(db_entity)
            self.db.commit()
            return db_entity
        return None

    def __del__(self):
        """Destructor method for the AbstractRepository class.

        This method is automatically called when the object is about to be destroyed.
        It closes the database connection.

        Note:
            It is generally recommended to explicitly close the database connection
            using the `close()` method before the object is destroyed.

        Raises:
            Any exceptions raised by the `close()` method of the database connection.

        """
        self.db.close()
