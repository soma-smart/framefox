from sqlmodel import SQLModel
from typing import Type
from pydantic import BaseModel, create_model
from sqlmodel import Field


class AbstractEntity(SQLModel):
    __abstract__ = True

    id: int = Field(default=None, primary_key=True)

    # @declared_attr
    # def __tablename__(cls):
    #     """
    #     Return the lowercase name of the class as the table name.

    #     Returns:
    #         str: The lowercase name of the class.
    #     """
    #     return cls.__name__.lower()

    # @classmethod
    # def generate_response_model(cls: Type[SQLModel]) -> Type[SQLModel]:
    #     """
    #     Generate the response model class.

    #     Returns:
    #         The response model class.
    #     """
    #     fields = {field.name: (field.type_, ...)
    #               for field in cls.__fields__.values()}
    #     response_model_class = create_model(
    #         f"{cls.__name__}Response", **fields)
    #     return response_model_class

    @classmethod
    def generate_create_model(cls) -> Type[BaseModel]:
        """
        Generate the create model class.

        Returns:
            The create model class.
        """
        fields = {name: (field.annotation, ...)
                  for name, field in cls.__fields__.items() if name != "id"}
        create_model_name = f"{cls.__name__}Create"
        create_model_class = create_model(create_model_name, **fields)
        return create_model_class
