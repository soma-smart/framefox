from abc import ABC
from sqlalchemy import asc, desc
from src.core.orm.config.database import db


class AbstractRepository(ABC):
    """
    AbstractRepository provides the following methods:

    - find(id): Retrieve an entity by its ID.
    - find_all(): Retrieve all entities.
    - add(entity): Add a new entity.
    - update(entity): Update an existing entity.
    - delete(entity): Delete an entity.
    - find_by(criteria): Retrieve entities based on specific criteria.
    """

    def __init__(self, model):
        """
        Initializes the repository with the given model.

        Args:
            model: The model class associated with the repository.
        """
        self.model = model

    def find_all(self):
        """
        Retrieves all items from the repository.

        Returns:
            A list of all items in the repository.
        """
        return self.model.query.all()

    def find(self, id):
        """
        Retrieves an item from the repository by its ID.

        Args:
            id: The ID of the item to retrieve.

        Returns:
            The item with the specified ID, or None if not found.
        """
        return self.model.query.get(id)

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
        query = self.model.query.filter_by(**criteria)

        if order_by:
            for key, value in order_by.items():
                if value.lower() == 'asc':
                    query = query.order_by(asc(getattr(self.model, key)))
                elif value.lower() == 'desc':
                    query = query.order_by(desc(getattr(self.model, key)))

        if limit:
            query = query.limit(limit)

        if offset:
            query = query.offset(offset)

        return query.all()

    def add(self, item):
        """
        Adds an item to the repository.

        Args:
            item: The item to add.
        """
        db.session.add(item)
        db.session.commit()

    def delete(self, item):
        """
        Deletes an item from the repository.

        Args:
            item: The item to delete.
        """
        db.session.delete(item)
        db.session.commit()
