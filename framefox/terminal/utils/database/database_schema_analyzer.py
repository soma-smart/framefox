from typing import Dict, List

from framefox.core.orm.migration.alembic_manager import AlembicManager
from sqlalchemy import create_engine, inspect

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class DatabaseSchemaAnalyzer:
    """
    Service responsible for analyzing database schema structure
    """

    def __init__(self, alembic_manager: AlembicManager):
        self.alembic_manager = alembic_manager

    def analyze_schema(self) -> Dict[str, Dict]:
        """
        Analyze database structure and return tables information

        Returns:
            Dict containing all tables with their columns, foreign keys and indexes
        """
        database_url = self.alembic_manager.get_database_url_string()
        engine = create_engine(database_url)
        inspector = inspect(engine)

        tables_info = {}
        table_names = inspector.get_table_names()

        for table_name in table_names:
            # Skip Alembic migration tables
            if table_name == "alembic_version":
                continue

            table_info = {
                "name": table_name,
                "columns": self._get_table_columns(inspector, table_name),
                "foreign_keys": self._get_table_foreign_keys(inspector, table_name),
                "indexes": self._get_table_indexes(inspector, table_name),
            }

            tables_info[table_name] = table_info

        # Close connection properly
        engine.dispose()
        return tables_info

    def _get_table_columns(self, inspector, table_name: str) -> List[Dict]:
        """
        Extract columns information from a table

        Args:
            inspector: SQLAlchemy inspector instance
            table_name: Name of the table to analyze

        Returns:
            List of column dictionaries with metadata
        """
        columns = []
        db_columns = inspector.get_columns(table_name)

        for column in db_columns:
            col_info = {
                "name": column["name"],
                "type": str(column["type"]),
                "nullable": column["nullable"],
                "primary_key": column.get("primary_key", False),
                "autoincrement": column.get("autoincrement", False),
                "default": column.get("default"),
            }
            columns.append(col_info)

        return columns

    def _get_table_foreign_keys(self, inspector, table_name: str) -> List[Dict]:
        """
        Extract foreign keys information from a table

        Args:
            inspector: SQLAlchemy inspector instance
            table_name: Name of the table to analyze

        Returns:
            List of foreign key dictionaries
        """
        foreign_keys = []
        db_fks = inspector.get_foreign_keys(table_name)

        for fk in db_fks:
            fk_info = {
                "name": fk["name"],
                "constrained_columns": fk["constrained_columns"],
                "referred_table": fk["referred_table"],
                "referred_columns": fk["referred_columns"],
            }
            foreign_keys.append(fk_info)

        return foreign_keys

    def _get_table_indexes(self, inspector, table_name: str) -> List[Dict]:
        """
        Extract indexes information from a table

        Args:
            inspector: SQLAlchemy inspector instance
            table_name: Name of the table to analyze

        Returns:
            List of index dictionaries
        """
        indexes = []
        db_indexes = inspector.get_indexes(table_name)

        for index in db_indexes:
            index_info = {
                "name": index["name"],
                "columns": index["column_names"],
                "unique": index["unique"],
            }
            indexes.append(index_info)

        return indexes
