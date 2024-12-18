from src.core.orm.abstract_repository import AbstractRepository
from src.entity.user import User


class UserRepository(AbstractRepository):
    def __init__(self):
        super().__init__(User)
