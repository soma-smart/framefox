import os
import secrets

from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.file_creator import FileCreator

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class CreateEnvCommand(AbstractCommand):
    """Command to generate a new .env file based on template"""

    def __init__(self):
        super().__init__("env")

    def execute(self):
        """Generate a new .env file with secure default values"""
        try:
            # Check if .env file already exists
            env_file_path = ".env"
            if os.path.exists(env_file_path):
                self.printer.print_msg(
                    "Error: .env file already exists!",
                    theme="error",
                    linebefore=True,
                )
                self.printer.print_msg(
                    "Remove the existing .env file before creating a new one.",
                    theme="info",
                )
                return

            # Generate secure session secret key
            session_secret_key = self._generate_secret_key()

            # Prepare template data
            template_data = {"session_secret_key": session_secret_key}

            # Create .env file using FileCreator and template
            file_creator = FileCreator()
            file_path = file_creator.create_file(template="init_files/env.jinja2", path=".", name=".env", data=template_data, format="env")

            self.printer.print_msg(
                f"✓ .env file created successfully: {file_path}",
                theme="success",
                linebefore=True,
            )
            self.printer.print_msg(
                "Remember to update the configuration values according to your environment.",
                theme="info",
            )

        except Exception as e:
            self.printer.print_msg(
                f"Error while creating .env file: {str(e)}",
                theme="error",
            )

    @staticmethod
    def _generate_secret_key():
        """Generate a random secret key of 32 bytes encoded in base64"""
        return secrets.token_urlsafe(32)
