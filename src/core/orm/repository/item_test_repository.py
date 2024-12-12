from src.core.orm.config.abstract_repository import AbstractRepository
from src.core.orm.entity.item_test import ItemTest


class ItemTestRepository(AbstractRepository):
    """
    Example
    """

    def __init__(self):
        super().__init__(ItemTest)
