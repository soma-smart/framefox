from src.core.orm.abstract_repository import AbstractRepository
from src.entity.user import User

"""
AbstractRepository provides the following methods:

- find(id): Retrieve an entity by its ID.
- find_all(): Retrieve all entities.
- find_by(criteria): Retrieve entities based on specific criteria.
- add(entity): Add a new entity.
- update(entity): Update an existing entity.
- delete(entity): Delete an entity.
"""


class UserRepository(AbstractRepository):
    def __init__(self):
        super().__init__(User)
