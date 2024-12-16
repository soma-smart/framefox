from sqlalchemy import Column, Integer, String
from src.core.orm.abstract_entity import AbstractEntity


class User(AbstractEntity):
    """
    Example
    """

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
