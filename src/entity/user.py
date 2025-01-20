from sqlmodel import Field, Column, JSON
from framefox.core.orm.abstract_entity import AbstractEntity
from typing import List
# from sqlalchemy import Column, JSON


class User(AbstractEntity, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(index=True, unique=True)
    password: str = Field()
    # user_identifier: str = email
    roles: List[str] = Field(
        default_factory=lambda: ["ROLE_USER"], sa_column=Column(JSON)
    )
