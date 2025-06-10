import os
from typing import Any, Dict, List

from framefox.core.orm.migration.alembic_manager import AlembicManager
from framefox.terminal.commands.database.abstract_database_command import (
    AbstractDatabaseCommand,
)

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
        self.output_path = "database"
        self.alembic_manager = AlembicManager()

    # def execute(self):
    #     """
    #     Generate a Mermaid diagram of the database schema by analyzing the DB directly
    #     """
    #     self.printer.print_msg(
    #         "Generating Mermaid diagram from database...",
    #         theme="bold_normal",
    #         linebefore=True,
    #     )

    #     try:
    #         # Analyze database structure
    #         tables_info = self._analyze_database_schema()

    #         if not tables_info:
    #             self.printer.print_msg(
    #                 "No tables found in the database",
    #                 theme="error",
    #                 linebefore=True,
    #                 newline=True,
    #             )
    #             return

    #         # Generate Mermaid code
    #         mermaid_code = self._generate_mermaid_diagram(tables_info)

    #         # Save to file
    #         self._save_diagram(mermaid_code)

    #     except Exception as e:
    #         self.printer.print_msg(
    #             f"Error generating diagram: {str(e)}",
    #             theme="error",
    #             linebefore=True,
    #             newline=True,
    #         )

    def execute(self):
        """
        Generate a Mermaid diagram of the database schema by analyzing the DB directly
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

            # Save to file
            self._save_diagram(mermaid_code)

            # Try terminal rendering first, fallback to web viewer
            # self._render_diagram_in_terminal(mermaid_code)
            self._open_web_viewer(mermaid_code)

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
        from sqlalchemy import create_engine, inspect

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
        # (multiple records from this table can reference one record in target table)

        # Check if FK column is unique (one-to-one relationship)
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
        # Generate a simple action name based on the foreign key column
        fk_column = fk["constrained_columns"][0]

        # Try to generate a meaningful action name
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
        # Remove common suffixes from FK column name
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

    def _save_diagram(self, mermaid_code: str):
        """
        Save Mermaid diagram to file
        """
        os.makedirs(self.output_path, exist_ok=True)
        output_file = os.path.join(self.output_path, "database_diagram.md")

        try:
            with open(output_file, "w", encoding="utf-8") as file:
                file.write("# Database Schema Diagram\n\n")
                file.write("This diagram was automatically generated from the database structure.\n\n")
                file.write("```mermaid\n")
                file.write(mermaid_code)
                file.write("\n```\n")

            self.printer.print_msg(
                f"✓ Mermaid diagram successfully generated: {output_file}",
                theme="success",
                linebefore=True,
                newline=True,
            )

        except Exception as e:
            self.printer.print_msg(
                f"Error saving diagram: {str(e)}",
                theme="error",
                linebefore=True,
                newline=True,
            )

    def _render_diagram_in_terminal(self, mermaid_code: str):
        """
        Render Mermaid diagram directly in terminal using mermaid-cli + image viewer
        """
        import os
        import subprocess
        import tempfile

        try:
            # Check if mermaid-cli is installed
            result = subprocess.run(["mmdc", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                raise FileNotFoundError("mermaid-cli not found")

            # Create temporary files
            with tempfile.NamedTemporaryFile(mode="w", suffix=".mmd", delete=False) as f:
                f.write(mermaid_code)
                mmd_file = f.name

            png_file = mmd_file.replace(".mmd", ".png")

            # Generate PNG image
            subprocess.run(
                [
                    "mmdc",
                    "-i",
                    mmd_file,
                    "-o",
                    png_file,
                    "-w",
                    "1200",  # Width
                    "-H",
                    "800",  # Height
                    "-b",
                    "white",  # Background
                    "-t",
                    "default",  # Theme
                ],
                check=True,
                capture_output=True,
            )

            # Try different terminal image viewers
            image_viewers = [
                ["chafa", png_file, "--size=100x40", "--colors=256"],
                ["catimg", png_file],
                ["img2txt", png_file],
                ["tiv", png_file],
                ["viu", png_file],
            ]

            displayed = False
            for viewer_cmd in image_viewers:
                try:
                    subprocess.run(viewer_cmd, check=True)
                    displayed = True
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue

            if not displayed:
                # Fallback: open with system image viewer
                if os.name == "nt":  # Windows
                    os.startfile(png_file)
                elif os.name == "posix":  # Linux/Mac
                    subprocess.run(["xdg-open", png_file], capture_output=True)

                self.printer.print_msg(f"✓ Diagram saved and opened: {png_file}", theme="success")
            else:
                self.printer.print_msg("✓ Diagram displayed in terminal", theme="success")

            # Cleanup
            os.unlink(mmd_file)
            # Keep PNG file for a while in case user wants to see it again

        except FileNotFoundError:
            self.printer.print_msg("⚠️  Terminal diagram display requires additional tools:", theme="warning", linebefore=True)
            self.printer.print_msg("   npm install -g @mermaid-js/mermaid-cli", theme="normal")
            self.printer.print_msg("   # And one of these image viewers:", theme="normal")
            self.printer.print_msg("   sudo apt install chafa      # Recommended", theme="normal")
            self.printer.print_msg("   pip install catimg          # Alternative", theme="normal")
            self.printer.print_msg("   cargo install viu           # Rust-based", theme="normal")
            return False

        except subprocess.CalledProcessError as e:
            self.printer.print_msg(f"Error rendering diagram: {e}", theme="error")
            return False

        return True

    def _open_web_viewer(self, mermaid_code: str):
        """
        Open a temporary web page with the Mermaid diagram
        """
        import os
        import tempfile
        import webbrowser
        from datetime import datetime

        # Enhanced HTML with better styling and features
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Database Schema - Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
            <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 15px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: #2c3e50;
                    color: white;
                    padding: 20px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 2em;
                }}
                .timestamp {{
                    opacity: 0.7;
                    font-size: 0.9em;
                    margin-top: 5px;
                }}
                .diagram-container {{
                    padding: 30px;
                    text-align: center;
                    background: white;
                }}
                .controls {{
                    margin-bottom: 20px;
                    text-align: center;
                }}
                button {{
                    background: #3498db;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    margin: 5px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 14px;
                    transition: background 0.3s;
                }}
                button:hover {{
                    background: #2980b9;
                }}
                .mermaid {{
                    background: white;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 20px 0;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                }}
                .footer {{
                    background: #ecf0f1;
                    padding: 15px;
                    text-align: center;
                    color: #7f8c8d;
                    font-size: 0.9em;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🗄️ Database Schema Diagram</h1>
                    <div class="timestamp">Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}</div>
                </div>
                
                <div class="diagram-container">
                    <div class="controls">
                        <button onclick="downloadSVG()">📥 Download SVG</button>
                        <button onclick="downloadPNG()">📥 Download PNG</button>
                        <button onclick="copyMermaidCode()">📋 Copy Mermaid Code</button>
                        <button onclick="toggleTheme()">🎨 Toggle Theme</button>
                    </div>
                    
                    <div class="mermaid" id="diagram">
    {mermaid_code}
                    </div>
                </div>
                
                <div class="footer">
                    Generated by Framefox Framework • 
                    <a href="https://mermaid.js.org/" target="_blank">Powered by Mermaid.js</a>
                </div>
            </div>

            <script>
                // Mermaid configuration
                mermaid.initialize({{ 
                    startOnLoad: true,
                    theme: 'default',
                    themeVariables: {{
                        primaryColor: '#3498db',
                        primaryTextColor: '#2c3e50',
                        primaryBorderColor: '#2980b9',
                        lineColor: '#34495e'
                    }}
                }});

                let currentTheme = 'default';
                const mermaidCode = `{mermaid_code}`;

                function downloadSVG() {{
                    const svg = document.querySelector('#diagram svg');
                    if (svg) {{
                        const svgData = new XMLSerializer().serializeToString(svg);
                        const svgBlob = new Blob([svgData], {{type: 'image/svg+xml;charset=utf-8'}});
                        const svgUrl = URL.createObjectURL(svgBlob);
                        const downloadLink = document.createElement('a');
                        downloadLink.href = svgUrl;
                        downloadLink.download = 'database_schema.svg';
                        document.body.appendChild(downloadLink);
                        downloadLink.click();
                        document.body.removeChild(downloadLink);
                    }}
                }}

                function downloadPNG() {{
                    const svg = document.querySelector('#diagram svg');
                    if (svg) {{
                        const canvas = document.createElement('canvas');
                        const ctx = canvas.getContext('2d');
                        const data = new XMLSerializer().serializeToString(svg);
                        const img = new Image();
                        const svgBlob = new Blob([data], {{ type: 'image/svg+xml;charset=utf-8' }});
                        const url = URL.createObjectURL(svgBlob);
                        
                        img.onload = function() {{
                            canvas.width = img.width;
                            canvas.height = img.height;
                            ctx.drawImage(img, 0, 0);
                            URL.revokeObjectURL(url);
                            
                            canvas.toBlob(function(blob) {{
                                const url = URL.createObjectURL(blob);
                                const downloadLink = document.createElement('a');
                                downloadLink.href = url;
                                downloadLink.download = 'database_schema.png';
                                document.body.appendChild(downloadLink);
                                downloadLink.click();
                                document.body.removeChild(downloadLink);
                                URL.revokeObjectURL(url);
                            }});
                        }};
                        img.src = url;
                    }}
                }}

                function copyMermaidCode() {{
                    navigator.clipboard.writeText(mermaidCode).then(function() {{
                        alert('Mermaid code copied to clipboard!');
                    }}, function(err) {{
                        console.error('Could not copy text: ', err);
                        // Fallback
                        const textArea = document.createElement('textarea');
                        textArea.value = mermaidCode;
                        document.body.appendChild(textArea);
                        textArea.select();
                        document.execCommand('copy');
                        document.body.removeChild(textArea);
                        alert('Mermaid code copied to clipboard!');
                    }});
                }}

                function toggleTheme() {{
                    const themes = ['default', 'dark', 'forest', 'neutral'];
                    const currentIndex = themes.indexOf(currentTheme);
                    currentTheme = themes[(currentIndex + 1) % themes.length];
                    
                    mermaid.initialize({{ 
                        startOnLoad: true,
                        theme: currentTheme
                    }});
                    
                    // Re-render diagram
                    const diagramDiv = document.getElementById('diagram');
                    diagramDiv.innerHTML = mermaidCode;
                    mermaid.init(undefined, diagramDiv);
                }}
            </script>
        </body>
        </html>
        """

        try:
            # # Create temporary HTML file
            # with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as f:
            #     f.write(html_content)
            #     html_file = f.name

            # # Open in default browser
            # webbrowser.open(f"file://{os.path.abspath(html_file)}")

            # Create output directory if it doesn't exist
            os.makedirs(self.output_path, exist_ok=True)

            # Generate filename with timestamp to avoid conflicts
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_filename = f"database_diagram_{timestamp}.html"
            html_file = os.path.join(self.output_path, html_filename)

            # Save HTML file locally
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            # Open in default browser
            webbrowser.open(f"file://{os.path.abspath(html_file)}")

            self.printer.print_msg(f"✓ Interactive diagram opened in browser", theme="success", linebefore=True)
            self.printer.print_msg(f"   File: {html_file}", theme="normal")
            self.printer.print_msg("   Features: Download SVG/PNG, Copy code, Change themes", theme="normal", newline=True)

            return True

        except Exception as e:
            self.printer.print_msg(f"Error opening web viewer: {str(e)}", theme="error")
            return False
