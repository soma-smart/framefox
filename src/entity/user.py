from sqlmodel import Field
from src.core.orm.abstract_entity import AbstractEntity


class User(AbstractEntity, table=True):
    """
    Example
    """

    name: str = Field(index=True)
