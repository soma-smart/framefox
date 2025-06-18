import contextlib
import logging
from typing import Any, Generator, Type

from sqlalchemy.orm.session import object_session
from sqlmodel import Session, SQLModel

from framefox.core.di.service_container import ServiceContainer
from framefox.core.orm.entity_manager_registry import EntityManagerRegistry

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël & BOUMAZA Rayen
Github: https://github.com/Vasulvius & https://github.com/RayenBou
"""


class EntityManager:
    """
    Entity manager scoped to the current request.
    """

    def __init__(self, connection_name: str = "default"):
        self.registry = EntityManagerRegistry.get_instance()
        self.logger = logging.getLogger(__name__)
        self.engine = self.registry.get_engine(connection_name)
        self._session = None
        self._transaction_depth = 0
        self._identity_map = {}

    @property
    def session(self) -> Session:
        """Returns the active session or creates a new one"""
        if self._session is None:
            self._session = Session(self.engine)
        return self._session

    def close_session(self):
        """Closes the active session if it exists"""
        if self._session is not None:
            self._session.close()
            self._session = None

    @contextlib.contextmanager
    def transaction(self) -> Generator[Session, None, None]:
        """Context manager for transactions"""
        session = self.session
        self._transaction_depth += 1
        try:
            yield session
            if self._transaction_depth == 1:
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self._transaction_depth -= 1

    def commit(self) -> None:
        """Commit if we are not in a nested transaction"""
        if self._transaction_depth <= 1:
            self.session.commit()

    def rollback(self) -> None:
        """Rolls back the current transaction"""
        self.session.rollback()

    def persist(self, entity):
        """
        Adds an entity to the session and identity map.
        If the entity already exists in the session, it merges it.
        """
        try:
            self.session.add(entity)
        except Exception as e:
            if "already attached to session" in str(e):
                try:
                    current_session = object_session(entity)
                    if current_session and current_session is not self.session:
                        current_session.expunge(entity)

                    entity = self.session.merge(entity)
                except Exception as merge_error:
                    self.logger.warning(f"Entity merge failed: {str(merge_error)}")
                    primary_keys = entity.get_primary_keys()
                    pk_value = (
                        getattr(entity, primary_keys[0]) if primary_keys else None
                    )

                    if pk_value:
                        fresh_entity = self.session.get(type(entity), pk_value)
                        if fresh_entity:
                            for attr, value in vars(entity).items():
                                if not attr.startswith("_") and hasattr(
                                    fresh_entity, attr
                                ):
                                    setattr(fresh_entity, attr, value)
                            entity = fresh_entity
                            self.session.add(entity)
            else:
                raise
        primary_keys = entity.get_primary_keys()
        if primary_keys:
            pk_name = primary_keys[0]
            pk_value = getattr(entity, pk_name)
            if pk_value:
                self._identity_map[(type(entity), pk_value)] = entity

        return entity

    def delete(self, entity) -> None:
        """
        Deletes the specified entity from the database session.
        """
        self.session.delete(entity)

    def refresh(self, entity) -> None:
        """
        Refresh the state of the given entity from the database, overwriting any local changes.
        This is useful when you want to ensure that the entity reflects the current state in the database.
        """
        self.session.refresh(entity)

    def exec_statement(self, statement) -> list:
        """
        Executes the given SQL statement and returns the result as a list.
        """
        return self.session.exec(statement).all()

    def find(self, entity_class, primary_key):
        """
        Retrieve an entity from the identity map or database session.

        This method first checks if the entity identified by the given class and primary key
        is present in the identity map. If found, it returns the cached entity. If not found,
        it queries the database session for the entity. If the entity is found in the database,
        it is added to the identity map and then returned.
        """
        map_key = (entity_class, primary_key)
        if map_key in self._identity_map:
            return self._identity_map[map_key]
        entity = self.session.get(entity_class, primary_key)
        if entity:
            self._identity_map[map_key] = entity
        return entity

    def find_existing_entity(self, entity) -> Any:
        """
        Finds an existing entity in the database.

        This method retrieves the primary keys of the given entity and uses them to
        search for the corresponding entity in the database.
        """
        primary_keys = entity.get_primary_keys()
        keys = {key: getattr(entity, key) for key in primary_keys}
        return self.find(entity.__class__, keys)

    def create_all_tables(self) -> None:
        """
        Create all tables in the database.

        This method uses the SQLModel metadata to create all tables defined in the
        models associated with this entity manager's engine. It ensures that the
        database schema is up-to-date with the current models.
        """
        SQLModel.metadata.create_all(self.engine)

    def drop_all_tables(self) -> None:
        """
        Drops all tables in the database.

        """
        SQLModel.metadata.drop_all(self.engine)

    def get_repository(self, entity_class: Type) -> Any:
        """
        Retrieve the repository instance associated with the given entity class.

        """
        repositories = ServiceContainer().get_by_tag_prefix("repository.")

        for repo in repositories:
            if getattr(repo, "model", None) == entity_class:
                return repo
        return None
