from src.core.orm.abstract_repository import AbstractRepository
from src.entity.item_test import ItemTest


class ItemTestRepository(AbstractRepository):
    """
    Example
    """

    def __init__(self):
        super().__init__(ItemTest)
