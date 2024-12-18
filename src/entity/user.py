from sqlmodel import Field
from src.core.orm.abstract_entity import AbstractEntity


class User(AbstractEntity, table=True):
    """
    Example
    """

    id: int = Field(default=None, primary_key=True)
    name: str = Field(index=True)
