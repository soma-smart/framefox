from typing import Optional
from unittest.mock import Mock, patch

import pytest
from sqlalchemy import MetaData
from sqlmodel import Field, SQLModel, select

from framefox.core.config.settings import Settings
from framefox.core.di.service_container import ServiceContainer
from framefox.core.orm.entity_manager import EntityManager
from framefox.core.orm.query_builder import QueryBuilder

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class TestQueryBuilder:
    @pytest.fixture(scope="function")
    def mock_settings(self):
        """Fixture for test settings"""
        settings = Mock(spec=Settings)
        settings.database_url = "sqlite:///:memory:"
        return settings

    @pytest.fixture(scope="function")
    def test_metadata(self):
        """Fixture for SQLAlchemy metadata"""
        metadata = MetaData()
        yield metadata
        metadata.clear()

    @pytest.fixture
    def mock_container(self, mock_settings):
        """Fixture for the service container"""
        container = ServiceContainer()
        container.get = Mock(return_value=mock_settings)

        with patch.object(ServiceContainer, "_instance", container):
            yield container

    @pytest.fixture
    def TestEntityClass(self, test_metadata):
        """Fixture for the test entity class"""

        class TestEntity(SQLModel, table=True):
            __tablename__ = f"test_entity_{id(test_metadata)}"
            metadata = test_metadata

            id: Optional[int] = Field(default=None, primary_key=True)
            name: str = Field(default="test")
            age: Optional[int] = Field(default=None)

            @classmethod
            def get_primary_keys(cls):
                """Returns the primary keys of the entity"""
                return ["id"]

        return TestEntity

    @pytest.fixture
    def entity_manager(self, mock_container, TestEntityClass):
        """Fixture for the EntityManager"""
        manager = EntityManager()
        # Create tables
        TestEntityClass.metadata.create_all(manager.engine)
        manager.session.commit()

        # Return the manager
        yield manager

        # Cleanup
        manager.session.rollback()
        manager.session.close()
        TestEntityClass.metadata.drop_all(manager.engine)

    @pytest.fixture
    def query_builder(self, entity_manager, TestEntityClass):
        """Fixture for the QueryBuilder"""
        return QueryBuilder(TestEntityClass, entity_manager)

    @pytest.fixture
    def test_data(self, entity_manager, TestEntityClass):
        """Fixture for test data"""
        entities = [
            TestEntityClass(name="Alice", age=25),
            TestEntityClass(name="Bob", age=30),
            TestEntityClass(name="Charlie", age=35),
        ]
        for entity in entities:
            entity_manager.persist(entity)
        entity_manager.session.commit()
        return entities

    def test_select_all(self, query_builder, test_data):
        """Test selecting all entities"""
        results = query_builder.select().execute()
        assert len(results) == 3
        assert all(isinstance(r, type(test_data[0])) for r in results)

    def test_select_with_where(self, query_builder, TestEntityClass, test_data):
        """Test selecting with WHERE condition"""
        results = query_builder.select().where(TestEntityClass.age > 30).execute()
        assert len(results) == 1
        assert results[0].name == "Charlie"

    def test_select_with_order_by(self, query_builder, TestEntityClass, test_data):
        """Test selecting with ORDER BY"""
        results = query_builder.select().order_by(TestEntityClass.age.desc()).execute()
        assert len(results) == 3
        assert results[0].age == 35
        assert results[-1].age == 25

    def test_select_with_limit(self, query_builder, test_data):
        """Test selecting with LIMIT"""
        results = query_builder.select().limit(2).execute()
        assert len(results) == 2

    def test_select_first(self, query_builder, TestEntityClass, test_data):
        """Test the first() method"""
        result = query_builder.select().order_by(TestEntityClass.name).first()
        assert result is not None
        assert result.name == "Alice"

    def test_update(self, query_builder, TestEntityClass, test_data):
        """Test updating"""
        query_builder.update({"age": 40}).where(
            TestEntityClass.name == "Alice"
        ).execute()
        result = query_builder.select().where(TestEntityClass.name == "Alice").first()
        assert result.age == 40
