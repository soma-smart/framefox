from sqlmodel import Field, Column, JSON
from framefox.core.orm.abstract_entity import AbstractEntity
from typing import List, Optional
from datetime import datetime


class Tata(AbstractEntity, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(max_length=256)
