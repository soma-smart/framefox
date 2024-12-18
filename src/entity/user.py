# from sqlalchemy import Column, Integer, String
# from src.core.orm.abstract_entity import AbstractEntity


# class User(AbstractEntity):
#     """
#     Example
#     """

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, index=True)


from sqlmodel import Field
from src.core.orm.abstract_entity import AbstractEntity

# from typing import Type
# from pydantic import BaseModel, create_model


class User(AbstractEntity, table=True):
    """
    Example
    """

    id: int = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    # @classmethod
    # def generate_create_model(cls) -> Type[BaseModel]:
    #     """
    #     Generate the create model class.

    #     Returns:
    #         The create model class.
    #     """
    #     fields = {name: (field.type_, ...)
    #               for name, field in cls.__fields__.items() if name != "id"}
    #     create_model_name = f"{cls.__name__}Create"
    #     create_model_class = create_model(create_model_name, **fields)
    #     return create_model_class
    # @classmethod
    # def generate_create_model(cls) -> Type[BaseModel]:
    #     """
    #     Generate the create model class.

    #     Returns:
    #         The create model class.
    #     """
    #     fields = {name: (field.annotation, ...)
    #               for name, field in cls.__fields__.items() if name != "id"}
    #     create_model_name = f"{cls.__name__}Create"
    #     create_model_class = create_model(create_model_name, **fields)
    #     return create_model_class


# class CreateUser(BaseModel):
#     name: str
