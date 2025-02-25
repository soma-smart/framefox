import logging
from typing import Any, Dict, List, Optional, Type

from sqlalchemy.sql.expression import Delete, Update
from sqlmodel import delete as sql_delete
from sqlmodel import select
from sqlmodel import update as sql_update

from framefox.core.orm.entity_manager import EntityManager

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class QueryBuilder:
    """
    QueryBuilder allows building and executing queries fluently for a single entity.
    """

    def __init__(self, model: Type[Any], entity_manager: EntityManager):
        self.entity_manager = entity_manager
        self.model = model
        self._select = None
        self._delete = None
        self._update = None
        self._where = []
        self._having = []
        self._order_by = []
        self._limit = None
        self._offset = None
        self._update_values = {}
        self.logger = logging.getLogger(__name__)

    def select(self) -> "QueryBuilder":
        self._select = select(self.model)
        return self

    def delete(self) -> "QueryBuilder":
        self._delete = sql_delete(self.model)
        return self

    def update(self, values: Dict[str, Any]) -> "QueryBuilder":
        self._update = sql_update(self.model).values(**values)
        return self

    def where(self, condition: Any) -> "QueryBuilder":
        self._where.append(condition)
        return self

    def join(self, *joins: Any) -> "QueryBuilder":
        if self._select is not None:
            self._select = self._select.join(*joins)
        elif self._delete is not None:
            self._delete = self._delete.join(*joins)
        elif self._update is not None:
            self._update = self._update.join(*joins)
        else:
            raise ValueError(
                "No query (select, delete, update) has been initiated.")
        return self

    def having(self, condition: Any) -> "QueryBuilder":
        self._having.append(condition)
        return self

    def order_by(self, *conditions: Any) -> "QueryBuilder":
        self._order_by.extend(conditions)
        return self

    def limit(self, limit: int) -> "QueryBuilder":
        self._limit = limit
        return self

    def offset(self, offset: int) -> "QueryBuilder":
        self._offset = offset
        return self

    def get_query(self) -> Any:
        query = None
        query_type = None

        if self._select is not None:
            query = self._select
            query_type = "select"
        elif self._delete is not None:
            query = self._delete
            query_type = "delete"
        elif self._update is not None:
            query = self._update
            query_type = "update"
        else:
            raise ValueError(
                "No query has been initiated (select, delete, update).")

        if self._where:
            query = query.where(*self._where)

        if self._having and query_type == "select":
            query = query.having(*self._having)

        if self._order_by:
            query = query.order_by(*self._order_by)

        if self._limit is not None:
            query = query.limit(self._limit)

        if self._offset is not None:
            query = query.offset(self._offset)

        return query

    def execute(self) -> List[Any]:
        query = self.get_query()
        with self.entity_manager.session as session:

            if isinstance(query, (Delete, Update)):
                result = session.exec(query)
                session.commit()
                return result
            else:
                result = session.exec(query).all()
                return result

    def first(self) -> Optional[Any]:
        query = self.get_query()
        with self.entity_manager.session as session:

            if isinstance(query, (Delete, Update)):
                raise ValueError(
                    "The 'first' method is not applicable for delete or update queries."
                )
            result = session.exec(query).first()
            return result

    def last(self) -> Optional[Any]:
        """
        Returns the last element of the query by reversing the current sort order.
        """
        query = self.get_query()

        if not self._order_by:
            raise ValueError(
                "A sort order must be defined to use the 'last' method.")

        reversed_order = []
        for condition in self._order_by:
            if hasattr(condition, "desc"):
                reversed_condition = condition.asc()
            elif hasattr(condition, "asc"):
                reversed_condition = condition.desc()
            else:
                raise ValueError(f"Unsupported order condition: {condition}")
            reversed_order.append(reversed_condition)

        query = query.order_by(*reversed_order).limit(1)

        with self.entity_manager.session as session:

            if isinstance(query, (Delete, Update)):
                raise ValueError(
                    "The 'last' method is not applicable for delete or update queries."
                )
            result = session.exec(query).first()
            return result
