from framefox.core.orm.migration.alembic_manager import AlembicManager
from framefox.terminal.commands.database.abstract_database_command import AbstractDatabaseCommand
from framefox.terminal.utils.database.database_schema_analyzer import DatabaseSchemaAnalyzer
from framefox.terminal.utils.database.diagram_file_generator import DiagramFileGenerator
from framefox.terminal.utils.database.mermaid_diagram_generator import MermaidDiagramGenerator

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class DiagramCommand(AbstractDatabaseCommand):
    """
    Command to generate Mermaid database schema diagrams

    This command orchestrates the database analysis, diagram generation,
    and file output processes using dedicated service classes.
    """

    def __init__(self):
        super().__init__()
        self.alembic_manager = AlembicManager()
        self.schema_analyzer = DatabaseSchemaAnalyzer(self.alembic_manager)
        self.diagram_generator = MermaidDiagramGenerator()
        self.file_generator = DiagramFileGenerator()

    def execute(self, no_browser: bool = False):
        """
        Generate a Mermaid diagram of the database schema.\n
        This method performs the following steps:\n
        1. Analyze the database structure to retrieve table information.\n
        2. Generate Mermaid code based on the analyzed schema.\n
        If no_browser is True, copy the Mermaid code to clipboard instead of opening a browser.

        Args:
            no_browser: If True, copy code to clipboard instead of opening browser
        """
        self.printer.print_msg(
            "Generating Mermaid diagram from database...",
            theme="bold_normal",
            linebefore=True,
        )

        try:
            tables_info = self.schema_analyzer.analyze_schema()

            if not tables_info:
                self.printer.print_msg(
                    "No tables found in the database",
                    theme="error",
                    linebefore=True,
                    newline=True,
                )
                return

            mermaid_code = self.diagram_generator.generate_diagram(tables_info)

            if no_browser:
                self.file_generator.copy_to_clipboard(mermaid_code)
            else:
                self.file_generator.generate_and_open_html(mermaid_code)

        except Exception as e:
            self.printer.print_msg(
                f"Error generating diagram: {str(e)}",
                theme="error",
                linebefore=True,
                newline=True,
            )
