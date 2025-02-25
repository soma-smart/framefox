from typing import Optional
from unittest.mock import Mock, patch

import pytest
from sqlmodel import Field, MetaData, SQLModel, select

from framefox.core.orm.abstract_entity import AbstractEntity
from framefox.core.orm.abstract_repository import AbstractRepository
from framefox.core.orm.entity_manager import EntityManager
from framefox.core.orm.query_builder import QueryBuilder

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class TestAbstractRepository:
    @pytest.fixture(scope="function")
    def test_metadata(self):
        """Fixture to create new metadata for each test"""
        meta = MetaData()
        yield meta
        meta.clear()

    @pytest.fixture
    def TestModel(self, test_metadata):
        """Fixture that creates a test model"""

        class User(AbstractEntity, table=True):
            """Test class inheriting from AbstractEntity"""

            __tablename__ = f"user_{id(test_metadata)}"

            # Metadata configuration via the Config class
            class Config:
                table = True
                metadata = test_metadata

            id: Optional[int] = Field(default=None, primary_key=True)
            name: str = Field(..., min_length=1)
            email: str = Field(..., min_length=1)
            age: Optional[int] = None

            @classmethod
            def generate_create_model(cls):
                return cls

        return User

    @pytest.fixture
    def mock_entity_manager(self):
        """Fixture that creates a mock of EntityManager"""
        manager = Mock(spec=EntityManager)
        manager.find = Mock()
        manager.exec_statement = Mock()
        return manager

    @pytest.fixture
    def repository(self, TestModel, mock_entity_manager):
        """Fixture that creates an instance of AbstractRepository"""
        with patch(
            "framefox.core.orm.abstract_repository.ServiceContainer"
        ) as MockContainer:
            container_instance = Mock()
            container_instance.get.return_value = mock_entity_manager
            MockContainer._instance = container_instance
            MockContainer.return_value = container_instance

            class TestRepository(AbstractRepository):
                def __init__(self):
                    super().__init__(TestModel)

            return TestRepository()

    def test_initialization(self, repository, TestModel):
        """Test repository initialization"""
        assert repository.model == TestModel
        assert repository.entity_manager is not None
        assert repository.create_model == TestModel

    def test_find(self, repository, mock_entity_manager):
        """Test the find method"""
        test_id = 1
        expected_result = repository.model(
            id=test_id, name="Test", email="test@test.com"
        )
        mock_entity_manager.find.return_value = expected_result

        result = repository.find(test_id)

        mock_entity_manager.find.assert_called_once_with(
            repository.model, test_id)
        assert result == expected_result

    def test_find_all(self, repository, mock_entity_manager):
        """Test the find_all method"""
        expected_results = [
            repository.model(id=1, name="Test1", email="test1@test.com"),
            repository.model(id=2, name="Test2", email="test2@test.com"),
        ]
        mock_entity_manager.exec_statement.return_value = expected_results

        results = repository.find_all()

        mock_entity_manager.exec_statement.assert_called_once()
        called_statement = mock_entity_manager.exec_statement.call_args[0][0]
        assert str(called_statement) == str(select(repository.model))
        assert results == expected_results

    def test_find_by(self, repository, mock_entity_manager):
        """Test the find_by method with different parameters"""
        expected_results = [repository.model(
            id=1, name="Test", email="test@test.com")]
        mock_entity_manager.exec_statement.return_value = expected_results

        # Test with simple criteria
        criteria = {"name": "Test"}
        results = repository.find_by(criteria)
        assert results == expected_results

        # Test with ascending order
        results = repository.find_by(criteria, order_by={"name": "asc"})
        assert results == expected_results

        # Test with descending order
        results = repository.find_by(criteria, order_by={"name": "desc"})
        assert results == expected_results

        # Test with limit and offset
        results = repository.find_by(criteria, limit=10, offset=0)
        assert results == expected_results

    def test_get_query_builder(self, repository):
        """Test the get_query_builder method"""
        query_builder = repository.get_query_builder()

        assert isinstance(query_builder, QueryBuilder)
        assert query_builder.model == repository.model
        assert query_builder.entity_manager == repository.entity_manager

    def test_find_by_with_invalid_order(self, repository, mock_entity_manager):
        """Test the find_by method with an invalid order"""
        # Configuration
        criteria = {"name": "Test"}
        order_by = {"name": "invalid"}

        # Simulate an error during query execution
        mock_entity_manager.exec_statement.side_effect = ValueError(
            "Invalid order direction 'invalid'. Must be 'asc' or 'desc'."
        )

        # Verify that the error is raised
        with pytest.raises(ValueError) as exc_info:
            repository.find_by(criteria, order_by=order_by)

        # Verify the error message
        assert "Invalid order direction" in str(exc_info.value)
        assert "Must be 'asc' or 'desc'" in str(exc_info.value)
