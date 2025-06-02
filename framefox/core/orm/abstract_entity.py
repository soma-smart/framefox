from typing import List, Type

from pydantic import BaseModel, create_model
from sqlmodel import SQLModel, inspect

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class AbstractEntity(SQLModel):
    __abstract__ = True

    @classmethod
    def generate_create_model(cls) -> Type[BaseModel]:
        """
        Generate the create model class.

        Returns:
            The create model class.
        """
        fields = {
            name: (field.annotation, ...)
            for name, field in cls.__fields__.items()
            if name != "id"
        }
        create_model_name = f"{cls.__name__}Create"
        create_model_class = create_model(create_model_name, **fields)
        return create_model_class

    @classmethod
    def get_primary_keys(cls: Type[SQLModel]) -> List[str]:
        """
        Return the list of primary key column names for the entity.

        Returns:
            List[str]: The list of primary key column names.
        """
        mapper = inspect(cls)
        primary_keys = [key.name for key in mapper.primary_key]
        return primary_keys

    @classmethod
    def generate_find_model(cls) -> Type[BaseModel]:
        """
        Generate the create model class.

        Returns:
            The create model class.
        """
        mapper = inspect(cls)
        primary_keys = [key.name for key in mapper.primary_key]
        fields = {
            name: (field.annotation, ...)
            for name, field in cls.__fields__.items()
            if name in primary_keys
        }
        create_model_name = f"{cls.__name__}Find"
        create_model_class = create_model(create_model_name, **fields)
        return create_model_class
