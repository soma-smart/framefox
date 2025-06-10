import os
import time
import webbrowser
from datetime import datetime
from typing import Dict, List

from sqlalchemy import create_engine, inspect

from framefox.core.orm.migration.alembic_manager import AlembicManager
from framefox.terminal.commands.database.abstract_database_command import (
    AbstractDatabaseCommand,
)
from framefox.terminal.common.file_creator import FileCreator

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class DiagramCommand(AbstractDatabaseCommand):
    def __init__(self):
        super().__init__("diagram")
        self.output_path = "temp"
        self.alembic_manager = AlembicManager()

    def execute(self, no_browser: bool = False):
        """
        Generate a Mermaid diagram of the database schema by analyzing the DB directly

        Args:
            no_browser: If True, generate only text file without opening browser
        """
        self.printer.print_msg(
            "Generating Mermaid diagram from database...",
            theme="bold_normal",
            linebefore=True,
        )

        try:
            # Analyze database structure
            tables_info = self._analyze_database_schema()

            if not tables_info:
                self.printer.print_msg(
                    "No tables found in the database",
                    theme="error",
                    linebefore=True,
                    newline=True,
                )
                return

            # Generate Mermaid code
            mermaid_code = self._generate_mermaid_diagram(tables_info)

            if no_browser:
                # Generate text file only
                self._save_mermaid_text_file(mermaid_code)
            else:
                # Generate HTML and open in browser
                self._generate_and_open_html(mermaid_code)

        except Exception as e:
            self.printer.print_msg(
                f"Error generating diagram: {str(e)}",
                theme="error",
                linebefore=True,
                newline=True,
            )

    def _analyze_database_schema(self) -> Dict[str, Dict]:
        """
        Analyze database structure directly via AlembicManager
        """

        # Use AlembicManager to get database URL
        database_url = self.alembic_manager.get_database_url_string()

        # Create engine and inspector
        engine = create_engine(database_url)
        inspector = inspect(engine)

        tables_info = {}

        # Get all tables
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

        # Close connection
        engine.dispose()

        return tables_info

    def _get_table_columns(self, inspector, table_name: str) -> List[Dict]:
        """
        Get columns of a table
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
        Get foreign keys of a table
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
        Get indexes of a table
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

    def _generate_mermaid_diagram(self, tables_info: Dict[str, Dict]) -> str:
        """
        Generate Mermaid code for ER diagram
        """
        mermaid_lines = ["erDiagram"]

        # First, generate all relationships
        for table_name, table_info in tables_info.items():
            entity_name = self._format_entity_name(table_name)

            for fk in table_info["foreign_keys"]:
                referred_entity = self._format_entity_name(fk["referred_table"])

                # Determine relationship type
                relationship_type = self._determine_relationship_type(table_name, fk, tables_info)

                # Generate relationship line
                relation_line = self._format_relationship_for_mermaid(entity_name, referred_entity, relationship_type, fk)

                if relation_line:
                    mermaid_lines.append(f"    {relation_line}")

        # Add empty line before entities
        mermaid_lines.append("")

        # Then generate all entities with their columns
        for table_name, table_info in tables_info.items():
            entity_name = self._format_entity_name(table_name)
            mermaid_lines.append(f"    {entity_name} {{")

            # Add columns in simple format
            for column in table_info["columns"]:
                col_line = self._format_column_for_mermaid(column)
                mermaid_lines.append(f"        {col_line}")

            mermaid_lines.append("    }")

        return "\n".join(mermaid_lines)

    def _format_entity_name(self, table_name: str) -> str:
        """
        Format table name to entity name (PascalCase)
        """
        # Convert snake_case to PascalCase
        parts = table_name.split("_")
        return "".join(word.capitalize() for word in parts)

    def _format_column_for_mermaid(self, column: Dict) -> str:
        """
        Format column for Mermaid display (simple format: type name)
        """
        col_type = self._simplify_sql_type(column["type"])
        return f"{col_type} {column['name']}"

    def _simplify_sql_type(self, sql_type: str) -> str:
        """
        Simplify SQL types for display
        """
        sql_type_upper = str(sql_type).upper()

        if "VARCHAR" in sql_type_upper or "TEXT" in sql_type_upper or "CHAR" in sql_type_upper:
            return "string"
        elif "INTEGER" in sql_type_upper or "INT" in sql_type_upper or "BIGINT" in sql_type_upper:
            return "int"
        elif "BOOLEAN" in sql_type_upper or "BOOL" in sql_type_upper:
            return "boolean"
        elif "DATETIME" in sql_type_upper or "TIMESTAMP" in sql_type_upper:
            return "datetime"
        elif "DATE" in sql_type_upper:
            return "date"
        elif "FLOAT" in sql_type_upper or "DECIMAL" in sql_type_upper or "NUMERIC" in sql_type_upper:
            return "float"
        else:
            return "string"

    def _determine_relationship_type(self, table_name: str, fk: Dict, tables_info: Dict) -> str:
        """
        Determine relationship type based on foreign key constraints
        """
        # By default, FK indicates many-to-one relationship
        table_info = tables_info[table_name]
        fk_column = fk["constrained_columns"][0]

        for index in table_info["indexes"]:
            if index["unique"] and fk_column in index["columns"]:
                return "one-to-one"

        return "many-to-one"

    def _format_relationship_for_mermaid(self, entity_name: str, referred_entity: str, relationship_type: str, fk: Dict) -> str:
        """
        Format relationship for Mermaid (simple format with action name)
        """
        fk_column = fk["constrained_columns"][0]
        action = self._generate_action_name(entity_name, referred_entity, fk_column)

        if relationship_type == "one-to-one":
            return f"{entity_name} ||--|| {referred_entity} : {action}"
        elif relationship_type == "many-to-one":
            return f"{entity_name} }}o--|| {referred_entity} : {action}"
        else:
            return f"{entity_name} }}o--o{{ {referred_entity} : {action}"

    def _generate_action_name(self, entity_name: str, referred_entity: str, fk_column: str) -> str:
        """
        Generate a meaningful action name for relationships
        """
        clean_column = fk_column.replace("_id", "").replace("id", "")

        # Common relationship patterns
        if "user" in entity_name.lower() and "order" in referred_entity.lower():
            return "places"
        elif "order" in entity_name.lower() and "user" in referred_entity.lower():
            return "belongs_to"
        elif "product" in entity_name.lower() and "category" in referred_entity.lower():
            return "belongs_to"
        elif "category" in referred_entity.lower():
            return "categorized_by"
        elif "user" in referred_entity.lower():
            return "owned_by"
        elif clean_column:
            return f"has_{clean_column}"
        else:
            return "references"

    def _save_mermaid_text_file(self, mermaid_code: str):
        """
        Save only the Mermaid code to a text file for copy-paste
        """
        # os.makedirs(self.output_path, exist_ok=True)
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # output_file = os.path.join(self.output_path, f"database_diagram_{timestamp}.txt")
        output_file = "database_diagram.txt"

        try:
            with open(output_file, "w", encoding="utf-8") as file:
                file.write(mermaid_code)

            self.printer.print_msg(
                f"✓ Mermaid code generated: {output_file}",
                theme="success",
                linebefore=True,
            )
            self.printer.print_msg(
                "  Copy the content and paste it in your Mermaid editor",
                theme="normal",
                newline=True,
            )

        except Exception as e:
            self.printer.print_msg(
                f"Error saving text file: {str(e)}",
                theme="error",
                linebefore=True,
                newline=True,
            )

    def _generate_and_open_html(self, mermaid_code: str):
        """
        Generate HTML file using template and open in browser
        """
        try:
            # Prepare template data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            formatted_timestamp = datetime.now().strftime("%Y-%m-%d at %H:%M:%S")

            template_data = {
                "mermaid_code": mermaid_code,
                "timestamp": timestamp,
                "formatted_timestamp": formatted_timestamp,
            }

            # Generate HTML file using FileCreator and template
            file_creator = FileCreator()
            html_file_path = file_creator.create_file(
                template="diagram_template.jinja2",
                path=".",
                name="database_diagram",
                data=template_data,
                format="html",
            )

            # Set proper permissions
            os.chmod(html_file_path, 0o644)

            # Open in default browser
            webbrowser.open(f"file://{os.path.abspath(html_file_path)}")

            time.sleep(2)  # Wait for browser to open
            # delete html_file_path
            os.remove(html_file_path)

            self.printer.print_msg(
                "✓ Interactive diagram opened in browser",
                theme="success",
                linebefore=True,
            )

        except Exception as e:
            self.printer.print_msg(
                f"Error generating HTML: {str(e)}",
                theme="error",
                linebefore=True,
                newline=True,
            )
