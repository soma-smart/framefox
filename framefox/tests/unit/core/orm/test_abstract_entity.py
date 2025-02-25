from typing import Optional

import pytest
from pydantic import BaseModel
from sqlmodel import Field

from framefox.core.orm.abstract_entity import AbstractEntity

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class TestUser(AbstractEntity, table=True):
    """Test class inheriting from AbstractEntity"""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)
    age: Optional[int] = None


class TestAbstractEntity:
    def test_generate_create_model(self):
        """Test the generation of the create model"""
        create_model = TestUser.generate_create_model()

        assert issubclass(create_model, BaseModel)
        assert create_model.__name__ == "TestUserCreate"

        # Check the fields
        fields = create_model.model_fields
        assert "name" in fields
        assert "email" in fields
        assert "age" in fields
        assert "id" not in fields  # id should not be included

        # Check the field types using annotation
        assert fields["name"].annotation == str
        assert fields["email"].annotation == str
        assert fields["age"].annotation == Optional[int]

    def test_generate_find_model(self):
        """Test the generation of the find model"""
        find_model = TestUser.generate_find_model()

        # Check that it is a Pydantic model
        assert issubclass(find_model, BaseModel)

        # Check the model name
        assert find_model.__name__ == "TestUserFind"

        # Check the fields
        fields = find_model.model_fields
        assert "id" in fields
        assert "name" not in fields
        assert "email" not in fields
        assert "age" not in fields

        assert fields["id"].annotation == Optional[int]

    def test_model_creation(self):
        """Test the creation of a model instance"""
        user_data = {"name": "Test User",
                     "email": "test@example.com", "age": 25}
        user = TestUser(**user_data)

        assert user.name == "Test User"
        assert user.email == "test@example.com"
        assert user.age == 25
        assert user.id is None
