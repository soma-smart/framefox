from typing import Dict

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class MermaidDiagramGenerator:
    """
    Service responsible for generating Mermaid ER diagram code from database schema
    """

    def generate_diagram(self, tables_info: Dict[str, Dict]) -> str:
        """
        Generate Mermaid ER diagram code from tables information

        Args:
            tables_info: Dictionary containing tables data from DatabaseSchemaAnalyzer

        Returns:
            Complete Mermaid diagram code as string
        """
        mermaid_lines = ["erDiagram"]

        # First, generate all relationships
        relationships = self._generate_relationships(tables_info)
        mermaid_lines.extend(relationships)

        # Add empty line before entities
        mermaid_lines.append("")

        # Then generate all entities with their columns
        entities = self._generate_entities(tables_info)
        mermaid_lines.extend(entities)

        return "\n".join(mermaid_lines)

    def _generate_relationships(self, tables_info: Dict[str, Dict]) -> list:
        """
        Generate relationship lines for the Mermaid diagram

        Args:
            tables_info: Dictionary containing tables data

        Returns:
            List of relationship lines
        """
        relationship_lines = []

        for table_name, table_info in tables_info.items():
            entity_name = self._format_entity_name(table_name)

            for fk in table_info["foreign_keys"]:
                referred_entity = self._format_entity_name(fk["referred_table"])

                # Determine relationship type
                relationship_type = self._determine_relationship_type(
                    table_name, fk, tables_info
                )

                # Generate relationship line
                relation_line = self._format_relationship_for_mermaid(
                    entity_name, referred_entity, relationship_type, fk
                )

                if relation_line:
                    relationship_lines.append(f"    {relation_line}")

        return relationship_lines

    def _generate_entities(self, tables_info: Dict[str, Dict]) -> list:
        """
        Generate entity definitions with columns for the Mermaid diagram

        Args:
            tables_info: Dictionary containing tables data

        Returns:
            List of entity definition lines
        """
        entity_lines = []

        for table_name, table_info in tables_info.items():
            entity_name = self._format_entity_name(table_name)
            entity_lines.append(f"    {entity_name} {{")

            # Add columns in simple format
            for column in table_info["columns"]:
                col_line = self._format_column_for_mermaid(column)
                entity_lines.append(f"        {col_line}")

            entity_lines.append("    }")

        return entity_lines

    def _format_entity_name(self, table_name: str) -> str:
        """
        Convert snake_case table name to PascalCase entity name

        Args:
            table_name: Snake case table name

        Returns:
            PascalCase entity name
        """
        parts = table_name.split("_")
        return "".join(word.capitalize() for word in parts)

    def _format_column_for_mermaid(self, column: Dict) -> str:
        """
        Format column for Mermaid display using simple 'type name' format

        Args:
            column: Column dictionary with metadata

        Returns:
            Formatted column string for Mermaid
        """
        col_type = self._simplify_sql_type(column["type"])
        return f"{col_type} {column['name']}"

    def _simplify_sql_type(self, sql_type: str) -> str:
        """
        Convert SQL types to simplified display types

        Args:
            sql_type: Original SQL type string

        Returns:
            Simplified type string for display
        """
        sql_type_upper = str(sql_type).upper()

        type_mapping = {
            "string": ["VARCHAR", "TEXT", "CHAR"],
            "int": ["INTEGER", "INT", "BIGINT"],
            "boolean": ["BOOLEAN", "BOOL"],
            "datetime": ["DATETIME", "TIMESTAMP"],
            "date": ["DATE"],
            "float": ["FLOAT", "DECIMAL", "NUMERIC"],
        }

        for display_type, sql_keywords in type_mapping.items():
            if any(keyword in sql_type_upper for keyword in sql_keywords):
                return display_type

        return "string"  # Default fallback

    def _determine_relationship_type(
        self, table_name: str, fk: Dict, tables_info: Dict
    ) -> str:
        """
        Determine relationship type based on foreign key constraints

        Args:
            table_name: Name of the table containing the FK
            fk: Foreign key information dictionary
            tables_info: All tables information

        Returns:
            Relationship type string ('one-to-one' or 'many-to-one')
        """
        table_info = tables_info[table_name]
        fk_column = fk["constrained_columns"][0]

        # Check if FK column has unique constraint (indicates one-to-one)
        for index in table_info["indexes"]:
            if index["unique"] and fk_column in index["columns"]:
                return "one-to-one"

        return "many-to-one"

    def _format_relationship_for_mermaid(
        self, entity_name: str, referred_entity: str, relationship_type: str, fk: Dict
    ) -> str:
        """
        Format relationship line for Mermaid diagram

        Args:
            entity_name: Source entity name
            referred_entity: Target entity name
            relationship_type: Type of relationship
            fk: Foreign key information

        Returns:
            Formatted Mermaid relationship line
        """
        fk_column = fk["constrained_columns"][0]
        action = self._generate_action_name(entity_name, referred_entity, fk_column)

        relationship_symbols = {
            "one-to-one": "||--||",
            "many-to-one": "}o--||",
            "default": "}o--o{",
        }

        symbol = relationship_symbols.get(
            relationship_type, relationship_symbols["default"]
        )
        return f"{entity_name} {symbol} {referred_entity} : {action}"

    def _generate_action_name(
        self, entity_name: str, referred_entity: str, fk_column: str
    ) -> str:
        """
        Generate meaningful action name for relationships based on entity names and context

        Args:
            entity_name: Source entity name
            referred_entity: Target entity name
            fk_column: Foreign key column name

        Returns:
            Action name for the relationship
        """
        clean_column = fk_column.replace("_id", "").replace("id", "")

        # Define common relationship patterns
        relationship_patterns = [
            (("user", "order"), "places"),
            (("order", "user"), "belongs_to"),
            (("product", "category"), "belongs_to"),
        ]

        # Check for specific patterns
        entity_lower = entity_name.lower()
        referred_lower = referred_entity.lower()

        for (source, target), action in relationship_patterns:
            if source in entity_lower and target in referred_lower:
                return action

        # Generic patterns based on target entity
        if "category" in referred_lower:
            return "categorized_by"
        elif "user" in referred_lower:
            return "owned_by"
        elif clean_column:
            return f"has_{clean_column}"
        else:
            return "references"
