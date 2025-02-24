import pytest
from unittest.mock import Mock, patch
from typing import Optional
from sqlmodel import Field, Session, create_engine, SQLModel, select
from sqlalchemy import MetaData
from framefox.core.orm.entity_manager import EntityManager
from framefox.core.config.settings import Settings
from framefox.core.di.service_container import ServiceContainer

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class TestEntityManager:
    """Tests for the EntityManager class"""

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
    def TestEntityClass(self, test_metadata):
        """Fixture for the test entity class"""
        class TestEntity(SQLModel, table=True):
            __tablename__ = f"test_entity_{id(test_metadata)}"
            metadata = test_metadata

            id: Optional[int] = Field(default=None, primary_key=True)
            name: str = Field(default="test")

            @classmethod
            def get_primary_keys(cls):
                return ["id"]

        return TestEntity

    @pytest.fixture
    def mock_container(self, mock_settings):
        """Fixture for the service container"""
        container = ServiceContainer()
        container.get = Mock(return_value=mock_settings)

        with patch.object(ServiceContainer, '_instance', container):
            yield container

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
    def test_entity(self, TestEntityClass):
        """Fixture for a test instance"""
        return TestEntityClass(name="test")

    # Initialization tests
    def test_initialization(self, entity_manager, mock_settings):
        """Test correct initialization of the EntityManager"""
        assert entity_manager.settings is mock_settings
        assert isinstance(entity_manager.engine, type(
            create_engine("sqlite:///:memory:")))
        assert isinstance(entity_manager.session, Session)
        assert entity_manager.logger is not None

    def test_get_instance_id(self, entity_manager):
        """Test instance ID generation"""
        assert isinstance(entity_manager.get_instance_id(), int)
        assert entity_manager.get_instance_id() == id(entity_manager)

    def test_persist_new_entity(self, entity_manager, test_entity):
        """Test persisting a new entity"""
        try:
            # Persist
            entity_manager.persist(test_entity)
            entity_manager.commit()

            # Verify the entity is in the session
            assert test_entity in entity_manager.session
            assert test_entity.id is not None

            # Reload from the database
            reloaded = entity_manager.find(type(test_entity), test_entity.id)
            assert reloaded is not None
            assert reloaded.name == test_entity.name
        finally:
            entity_manager.session.rollback()

    def test_persist_existing_entity(self, entity_manager, test_entity):
        """Test updating an existing entity"""
        try:
            # Create the entity
            entity_manager.persist(test_entity)
            entity_manager.commit()
            original_id = test_entity.id

            # Modify and update
            test_entity.name = "updated"
            entity_manager.persist(test_entity)
            entity_manager.session.commit()

            # Verify the ID has not changed
            assert test_entity.id == original_id
            assert test_entity.name == "updated"

            # Reload from the database
            reloaded = entity_manager.find(type(test_entity), test_entity.id)
            assert reloaded.name == "updated"
        finally:
            entity_manager.session.rollback()

    def test_delete_entity(self, entity_manager, test_entity):
        """Test deleting an entity"""
        try:
            # Persist the entity
            entity_manager.persist(test_entity)
            entity_manager.commit()
            entity_id = test_entity.id

            # Delete the entity
            entity_manager.delete(test_entity)
            entity_manager.session.commit()

            # Verify the entity no longer exists
            deleted = entity_manager.find(type(test_entity), entity_id)
            assert deleted is None
        finally:
            entity_manager.session.rollback()

    def test_refresh_entity(self, entity_manager, test_entity):
        """Test refreshing an entity"""
        try:
            # Persist the entity
            entity_manager.persist(test_entity)
            entity_manager.commit()

            original_name = test_entity.name
            test_entity.name = "modified"

            # Refresh the entity
            entity_manager.refresh(test_entity)
            assert test_entity.name == original_name
        finally:
            entity_manager.session.rollback()

    def test_exec_statement(self, entity_manager, TestEntityClass):
        """Test executing a SQL statement"""
        # Create test data
        entities = [
            TestEntityClass(name="test1"),
            TestEntityClass(name="test2")
        ]
        for entity in entities:
            entity_manager.persist(entity)

        # Test the query
        statement = select(TestEntityClass).order_by(TestEntityClass.name)
        results = list(entity_manager.exec_statement(statement))

        assert len(results) == 2
        assert results[0].name == "test1"
        assert results[1].name == "test2"

    def test_find_by_id(self, entity_manager, test_entity):
        """Test finding by ID"""
        try:
            # Persist the entity
            entity_manager.persist(test_entity)
            entity_manager.commit()

            # Verify the entity has an ID after persisting
            assert test_entity.id is not None

            # Find the entity by its ID
            found = entity_manager.find(type(test_entity), test_entity.id)
            assert found is not None
            assert found.id == test_entity.id
            assert found.name == test_entity.name
        finally:
            entity_manager.session.rollback()
