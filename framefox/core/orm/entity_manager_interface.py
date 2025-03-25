from typing import Any, Generator, Type
import contextlib
from sqlmodel import Session
from framefox.core.request.request_stack import RequestStack
from framefox.core.orm.entity_manager import EntityManager


class EntityManagerInterface:
    """
    Interface that delegates calls to the EntityManager specific to the current request.
    Can be injected into the constructor of controllers.
    """

    def _get_current_entity_manager(self):
        """
        Retrieves the EntityManager linked to the current request,
        or creates a new one if we are out of HTTP context
        """
        current_request = RequestStack.get_request()
        if current_request and hasattr(current_request.state, "entity_manager"):
            return current_request.state.entity_manager

        # Fallback for non-HTTP contexts (CLI, tests, etc.)

        return EntityManager()

    @property
    def session(self) -> Session:
        return self._get_current_entity_manager().session

    def close_session(self):
        return self._get_current_entity_manager().close_session()

    @contextlib.contextmanager
    def transaction(self) -> Generator[Session, None, None]:
        with self._get_current_entity_manager().transaction() as session:
            yield session

    def commit(self) -> None:
        return self._get_current_entity_manager().commit()

    def rollback(self) -> None:
        return self._get_current_entity_manager().rollback()

    def persist(self, entity) -> None:
        return self._get_current_entity_manager().persist(entity)

    def delete(self, entity) -> None:
        return self._get_current_entity_manager().delete(entity)

    def refresh(self, entity) -> None:
        return self._get_current_entity_manager().refresh(entity)

    def exec_statement(self, statement) -> list:
        return self._get_current_entity_manager().exec_statement(statement)

    def find(self, entity_class, primary_keys) -> Any:
        return self._get_current_entity_manager().find(entity_class, primary_keys)

    def find_existing_entity(self, entity) -> Any:
        return self._get_current_entity_manager().find_existing_entity(entity)

    def create_all_tables(self) -> None:
        return self._get_current_entity_manager().create_all_tables()

    def drop_all_tables(self) -> None:
        return self._get_current_entity_manager().drop_all_tables()

    def get_repository(self, entity_class: Type) -> Any:
        return self._get_current_entity_manager().get_repository(entity_class)
