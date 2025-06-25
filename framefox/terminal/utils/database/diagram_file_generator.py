import os
import time
import webbrowser
from datetime import datetime

from framefox.terminal.common.file_creator import FileCreator
from framefox.terminal.common.printer import Printer

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class DiagramFileGenerator:
    """
    Service responsible for generating and managing diagram output files
    """

    def __init__(self, output_path: str = "temp"):
        self.output_path = output_path
        self.printer = Printer()

    def copy_to_clipboard(self, mermaid_code: str) -> bool:
        """
        Copy Mermaid code to system clipboard

        Args:
            mermaid_code: The Mermaid diagram code to copy

        Returns:
            True if successful, False otherwise
        """
        try:
            import pyperclip

            pyperclip.copy(mermaid_code)

            self.printer.print_msg(
                "✓ Mermaid code copied to clipboard!",
                theme="success",
                linebefore=True,
            )
            self.printer.print_msg(
                "  Press Ctrl+V to paste it in your Mermaid editor",
                theme="normal",
                newline=True,
            )
            return True

        except ImportError:
            return self._fallback_clipboard_copy(mermaid_code)

    def _fallback_clipboard_copy(self, mermaid_code: str) -> bool:
        """
        Fallback clipboard copy using system commands

        Args:
            mermaid_code: The Mermaid diagram code to copy

        Returns:
            True if successful, False otherwise
        """
        try:
            import platform
            import subprocess

            system = platform.system()
            commands = {
                "Linux": [
                    ["xclip", "-selection", "clipboard"],
                    ["xsel", "--clipboard", "--input"],
                ],
                "Darwin": [["pbcopy"]],  # macOS
                "Windows": [["clip"]],
            }

            if system not in commands:
                return self._save_to_file_fallback(mermaid_code)

            # Try each command for the current system
            for cmd in commands[system]:
                try:
                    subprocess.run(cmd, input=mermaid_code, text=True, check=True)

                    self.printer.print_msg(
                        f"✓ Mermaid code copied to clipboard using {cmd[0]}!",
                        theme="success",
                        linebefore=True,
                    )
                    self.printer.print_msg(
                        "  Press Ctrl+V to paste it in your Mermaid editor",
                        theme="normal",
                        newline=True,
                    )
                    return True

                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue

            # If all commands failed
            return self._save_to_file_fallback(mermaid_code)

        except Exception:
            return self._save_to_file_fallback(mermaid_code)

    def _save_to_file_fallback(self, mermaid_code: str) -> bool:
        """
        Final fallback: save to file when clipboard is not available

        Args:
            mermaid_code: The Mermaid diagram code to save

        Returns:
            True if successful, False otherwise
        """
        try:
            self.printer.print_msg(
                "⚠️  Could not copy to clipboard. Saving to file instead...",
                theme="warning",
                linebefore=True,
            )

            output_file = "database_diagram.txt"

            with open(output_file, "w", encoding="utf-8") as file:
                file.write(mermaid_code)

            self.printer.print_msg(
                f"✓ Mermaid code saved: {output_file}",
                theme="success",
            )
            self.printer.print_msg(
                "  Install pyperclip for clipboard support: pip install pyperclip",
                theme="normal",
                newline=True,
            )
            return True

        except Exception as e:
            self.printer.print_msg(
                f"Error saving to file: {str(e)}",
                theme="error",
                linebefore=True,
                newline=True,
            )
            return False

    def generate_and_open_html(self, mermaid_code: str) -> bool:
        """
        Generate HTML file using template and open in browser

        Args:
            mermaid_code: The Mermaid diagram code to embed

        Returns:
            True if successful, False otherwise
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

            # Set proper file permissions
            os.chmod(html_file_path, 0o644)

            # Open in default browser
            webbrowser.open(f"file://{os.path.abspath(html_file_path)}")

            time.sleep(2)  # Wait for browser to open
            os.remove(html_file_path)  # Clean up temporary file

            self.printer.print_msg(
                "✓ Interactive diagram opened in browser",
                theme="success",
                linebefore=True,
            )
            return True

        except Exception as e:
            self.printer.print_msg(
                f"Error generating HTML: {str(e)}",
                theme="error",
                linebefore=True,
                newline=True,
            )
            return False
